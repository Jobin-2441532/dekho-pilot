import os
import uuid
import shutil
from pathlib import Path
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.core.config import settings
from app.models import UploadedFile, RawRecord, User
from app.services.parsers.pdf_parser import parse_pdf
from app.services.parsers.csv_parser import parse_csv
from app.services.parsers.sms_parser import parse_sms
from app.services.normalization import normalization_service
from app.services.storage import storage_service

router = APIRouter()

# Ensure upload directory exists
UPLOAD_DIR = Path(settings.DATA_DIR) / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


class SMSPasteRequest(BaseModel):
    text: str


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a PDF or CSV bank statement. File is saved locally, parsed, and
    transactions are inserted into the database automatically.
    """
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in (".pdf", ".csv"):
        raise HTTPException(status_code=400, detail="Only PDF and CSV files are supported.")

    # Get user (prototype: use first user)
    user = db.query(User).first()
    uid = user.id if user else 1

    # Save file locally
    file_id = str(uuid.uuid4())
    safe_filename = f"{file_id}{ext}"
    file_path = UPLOAD_DIR / safe_filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Create DB record
    uploaded_file = UploadedFile(
        user_id=uid,
        filename=file.filename,
        s3_key=str(file_path),  # Will be updated to MinIO key below
        file_type="pdf" if ext == ".pdf" else "csv",
        status="parsing"
    )
    db.add(uploaded_file)
    db.commit()
    db.refresh(uploaded_file)

    # Upload to MinIO (non-blocking — fall back to local path if unavailable)
    content_type = "application/pdf" if ext == ".pdf" else "text/csv"
    try:
        minio_key = storage_service.upload_file(
            user_id=uid,
            file_id=file_id,
            local_path=file_path,
            content_type=content_type,
        )
        uploaded_file.s3_key = minio_key
        db.commit()
    except Exception as minio_err:
        print(f"⚠️  MinIO upload skipped (using local path): {minio_err}")

    # Parse the file
    try:
        if ext == ".pdf":
            parsed_rows = parse_pdf(file_path)
        else:
            parsed_rows = parse_csv(file_path)

        # Normalize and insert transactions
        created = normalization_service.normalize(
            db=db,
            user_id=uid,
            parsed_rows=parsed_rows,
            source_type=uploaded_file.file_type,
            source_reference_id=uploaded_file.id,
        )

        uploaded_file.status = "completed"
        db.commit()

        return {
            "message": "File uploaded and parsed successfully",
            "file_id": uploaded_file.id,
            "transactions_created": len(created),
            "status": "completed",
        }

    except Exception as e:
        uploaded_file.status = "failed"
        db.commit()
        raise HTTPException(status_code=500, detail=f"Parsing failed: {str(e)}")


@router.get("/files")
def list_uploaded_files(db: Session = Depends(get_db)):
    """List all uploaded files for the current user."""
    user = db.query(User).first()
    uid = user.id if user else 1

    files = db.query(UploadedFile).filter(UploadedFile.user_id == uid).order_by(UploadedFile.id.desc()).all()
    return [
        {
            "id": f.id,
            "filename": f.filename,
            "file_type": f.file_type,
            "status": f.status,
            "uploaded_at": str(f.created_at) if hasattr(f, "created_at") else None,
        }
        for f in files
    ]


@router.post("/sms/paste")
async def paste_sms(
    request: SMSPasteRequest,
    db: Session = Depends(get_db)
):
    """
    Accepts a raw block of copied SMS messages, stores each as a RawRecord,
    then immediately attempts to parse all pending records.
    """
    user = db.query(User).first()
    uid = user.id if user else 1

    # Split by double newline or long dashes
    messages = [m.strip() for m in request.text.split('\n\n') if m.strip()]

    records = []
    for msg in messages:
        record = RawRecord(
            user_id=uid,
            source_type="sms",
            raw_data=msg,
            parsed_status="pending"
        )
        db.add(record)
        records.append(record)

    db.commit()

    # Auto-trigger parsing immediately
    parsed_count = _parse_pending_sms(db, uid)

    return {
        "message": f"Received {len(records)} SMS messages, parsed {parsed_count} transactions.",
        "received": len(records),
        "transactions_created": parsed_count,
    }


@router.post("/sms/parse")
async def trigger_sms_parse(db: Session = Depends(get_db)):
    """Manually trigger parsing of all pending SMS RawRecords."""
    user = db.query(User).first()
    uid = user.id if user else 1
    parsed_count = _parse_pending_sms(db, uid)
    return {"message": f"Parsed {parsed_count} transactions from pending SMS records."}


@router.get("/sms/history")
def sms_history(db: Session = Depends(get_db)):
    """List all stored SMS raw records."""
    user = db.query(User).first()
    uid = user.id if user else 1

    records = db.query(RawRecord).filter(
        RawRecord.user_id == uid,
        RawRecord.source_type == "sms"
    ).order_by(RawRecord.id.desc()).all()

    return [
        {
            "id": r.id,
            "text": r.raw_data,
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
        RawRecord.parsed_status == "pending"
    ).all()

    total_created = 0
    for record in pending:
        parsed = parse_sms(record.raw_data)
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

