import os
import uuid
import shutil
import logging
from pathlib import Path
from typing import List
from fastapi import APIRouter, BackgroundTasks, Depends, Request, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import httpx

from app.core.database import get_db, SessionLocal
from app.core.config import settings
from app.core.security import validate_upload, sanitise_sms
from app.core.rate_limit import limiter
from app.models import UploadedFile, RawRecord, User, Transaction
from app.services.parsers.pdf_parser import parse_pdf
from app.services.parsers.csv_parser import parse_csv
from app.services.parsers.sms_parser import parse_sms
from app.services.normalization import normalization_service
from app.services.storage import storage_service
from app.api.endpoints.auth import get_current_user

logger = logging.getLogger("dekho.ingestion")
ML_SERVICE_URL = os.getenv("ML_SERVICE_URL", "http://localhost:8001")

router = APIRouter()

# Ensure upload directory exists
UPLOAD_DIR = Path(settings.DATA_DIR) / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


class SMSPasteRequest(BaseModel):
    text: str


# ---------------------------------------------------------------------------
# ML enrichment background task
# ---------------------------------------------------------------------------
async def _enrich_with_ml(transaction_ids: List[int], user_id: int) -> None:
    """
    Fire-and-forget: calls ML sidecar to reclassify newly created transactions.
    Runs in background — main upload response is not blocked.
    Updates category/confidence in place if ML returns a better classification.
    """
    db = SessionLocal()
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            for tx_id in transaction_ids:
                tx = db.query(Transaction).filter(
                    Transaction.id == tx_id,
                    Transaction.user_id == user_id,
                ).first()
                if not tx:
                    continue

                # Build SMS-like text for the classifier
                desc = tx.merchant or ""
                sms_text = (
                    f"{tx.direction.upper() if tx.direction else 'DEBIT'}: "
                    f"Rs {tx.amount} to {desc} via {tx.payment_mode or 'UPI'}"
                )

                try:
                    r = await client.post(
                        f"{ML_SERVICE_URL}/api/sms/ingest",
                        json={"user_id": user_id, "sms_text": sms_text},
                    )
                    if r.status_code == 200:
                        ml_result = r.json()
                        # Only update if ML has higher confidence than existing
                        ml_confidence = ml_result.get("confidence", 0.0)
                        if ml_confidence > (tx.confidence or 0.0):
                            tx.category = ml_result.get("category", tx.category)
                            tx.sub_category = ml_result.get("sub_category", tx.sub_category)
                            tx.confidence = ml_confidence
                            if ml_result.get("merchant"):
                                tx.merchant = ml_result["merchant"]
                        db.commit()
                except Exception:
                    pass  # Non-fatal — keep original classification
    except Exception as e:
        logger.warning(f"ML enrichment background task failed: {e}")
    finally:
        db.close()


# ---------------------------------------------------------------------------
# POST /upload  — rate limited: 10 uploads/minute per IP
# ---------------------------------------------------------------------------
@router.post("/upload")
@limiter.limit("10/minute")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload a PDF or CSV bank statement.
    - File type and size are validated before writing to disk.
    - File is saved locally and optionally to MinIO (key is never exposed in response).
    - Transactions are inserted automatically.
    """
    # Read file content to check size BEFORE writing to disk
    content = await file.read()
    file_size = len(content)

    # Validate type + size
    try:
        validate_upload(file.filename, file.content_type, file_size)
    except ValueError as ve:
        raise HTTPException(status_code=422, detail=str(ve))

    ext = os.path.splitext(file.filename)[1].lower()
    file_id = str(uuid.uuid4())
    safe_filename = f"{file_id}{ext}"
    file_path = UPLOAD_DIR / safe_filename

    # Write to local disk
    with open(file_path, "wb") as buffer:
        buffer.write(content)

    # Create DB record — storage_path is safe name internally, never exposed in response
    uploaded_file = UploadedFile(
        user_id=current_user.id,
        filename=file.filename,         # original name for display only
        file_size=file_size,
        file_type="pdf" if ext == ".pdf" else "csv",
        storage_path=safe_filename,
        status="parsing",
    )
    db.add(uploaded_file)
    db.commit()
    db.refresh(uploaded_file)

    # Upload to MinIO — key stored in DB but never returned to client
    content_type = "application/pdf" if ext == ".pdf" else "text/csv"
    try:
        minio_key = storage_service.upload_file(
            user_id=current_user.id,
            file_id=file_id,
            local_path=file_path,
            content_type=content_type,
        )
        uploaded_file.s3_key = minio_key
        db.commit()
    except Exception:
        pass   # Non-fatal: parsing continues from local copy

    # Parse and normalise
    try:
        if ext == ".pdf":
            parsed_rows = parse_pdf(file_path)
        else:
            parsed_rows = parse_csv(file_path)

        created = normalization_service.normalize(
            db=db,
            user_id=current_user.id,
            parsed_rows=parsed_rows,
            source_type=uploaded_file.file_type,
            source_reference_id=uploaded_file.id,
        )

        uploaded_file.status = "completed"
        db.commit()

        # ── ML Enrichment (background, non-blocking) ──
        # Fire-and-forget: re-classifies transactions via ML sidecar.
        # Only updates if ML confidence > normalization confidence.
        if created and background_tasks is not None:
            tx_ids = [tx.id for tx in created if hasattr(tx, "id")]
            if tx_ids:
                background_tasks.add_task(_enrich_with_ml, tx_ids, current_user.id)

        return {
            "message": "File uploaded and parsed successfully",
            "file_id": uploaded_file.id,
            "filename": uploaded_file.filename,
            "transactions_created": len(created),
            "status": "completed",
            "ml_enrichment": "queued" if created else "skipped",
            # NOTE: no s3_key, no storage_path, no local file path in response
        }

    except Exception as e:
        uploaded_file.status = "failed"
        db.commit()
        raise HTTPException(status_code=500, detail=f"Parsing failed: {str(e)}")


# ---------------------------------------------------------------------------
# GET /files — JWT scoped, no internal paths exposed
# ---------------------------------------------------------------------------
@router.get("/files")
def list_uploaded_files(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all uploaded files for the authenticated user (no internal paths)."""
    files = (
        db.query(UploadedFile)
        .filter(UploadedFile.user_id == current_user.id)
        .order_by(UploadedFile.id.desc())
        .all()
    )
    return [
        {
            "id": f.id,
            "filename": f.filename,
            "file_type": f.file_type,
            "file_size_kb": round(f.file_size / 1024, 1) if f.file_size else None,
            "status": f.status,
            "uploaded_at": str(f.created_at) if f.created_at else None,
            # storage_path and s3_key intentionally omitted
        }
        for f in files
    ]


# ---------------------------------------------------------------------------
# POST /sms/paste — rate limited: 20/minute, SMS sanitised before storage
# ---------------------------------------------------------------------------
@router.post("/sms/paste")
@limiter.limit("20/minute")
async def paste_sms(
    request: Request,
    body: SMSPasteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Accepts a raw block of copied SMS messages.
    Text is sanitised (strips HTML/scripts/control chars) before storage.
    """
    raw_messages = [m.strip() for m in body.text.split("\n\n") if m.strip()]

    if not raw_messages:
        raise HTTPException(status_code=422, detail="No SMS text found. Paste one or more SMS messages.")

    if len(raw_messages) > 200:
        raise HTTPException(status_code=422, detail="Too many messages at once. Paste up to 200 SMS.")

    records = []
    for msg in raw_messages:
        clean = sanitise_sms(msg)
        if not clean:
            continue
        record = RawRecord(
            user_id=current_user.id,
            source_type="sms",
            raw_text=clean,
            raw_data=clean,
            parsed_status="pending",
        )
        db.add(record)
        records.append(record)

    db.commit()
    parsed_count = _parse_pending_sms(db, current_user.id)

    return {
        "message": f"Received {len(records)} SMS messages, parsed {parsed_count} transactions.",
        "received": len(records),
        "transactions_created": parsed_count,
    }


# ---------------------------------------------------------------------------
# POST /sms/parse — JWT scoped
# ---------------------------------------------------------------------------
@router.post("/sms/parse")
async def trigger_sms_parse(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Manually trigger parsing of all pending SMS RawRecords for the authenticated user."""
    parsed_count = _parse_pending_sms(db, current_user.id)
    return {"message": f"Parsed {parsed_count} transactions from pending SMS records."}


# ---------------------------------------------------------------------------
# GET /sms/history — JWT scoped, preview only (no raw text dump)
# ---------------------------------------------------------------------------
@router.get("/sms/history")
def sms_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List SMS raw records for the authenticated user (preview only)."""
    records = (
        db.query(RawRecord)
        .filter(
            RawRecord.user_id == current_user.id,
            RawRecord.source_type == "sms",
        )
        .order_by(RawRecord.id.desc())
        .all()
    )
    return [
        {
            "id": r.id,
            "preview": ((r.raw_data or r.raw_text or "")[:80] + "…"),
            "status": r.parsed_status,
        }
        for r in records
    ]


# ---------------------------------------------------------------------------
# Internal helper
# ---------------------------------------------------------------------------
def _parse_pending_sms(db: Session, user_id: int) -> int:
    """Parse all pending SMS records for a user and return transaction count."""
    pending = db.query(RawRecord).filter(
        RawRecord.user_id == user_id,
        RawRecord.source_type == "sms",
        RawRecord.parsed_status == "pending",
    ).all()

    total_created = 0
    for record in pending:
        raw = record.raw_data or record.raw_text
        parsed = parse_sms(raw)
        if parsed:
            normalization_service.normalize(
                db=db,
                user_id=user_id,
                parsed_rows=[parsed],
                source_type="sms",
                source_reference_id=record.id,
            )
            record.parsed_status = "processed"
            total_created += 1
        else:
            record.parsed_status = "unrecognised"

    db.commit()
    return total_created
