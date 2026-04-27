"""
Celery tasks for file parsing (PDF/CSV) and SMS parsing.
These run asynchronously in the background so the upload endpoint
returns immediately and the user gets a job_id to poll.
"""
from app.celery_app import celery_app
from app.core.database import SessionLocal
from app.models import UploadedFile, RawRecord
from app.services.parsers.pdf_parser import parse_pdf
from app.services.parsers.csv_parser import parse_csv
from app.services.parsers.sms_parser import parse_sms
from app.services.normalization import normalization_service


@celery_app.task(bind=True, name="tasks.parse_file")
def parse_file_task(self, uploaded_file_id: int, user_id: int):
    """
    Async task: parse a PDF or CSV uploaded file and create transactions.
    
    Args:
        uploaded_file_id: PK of the UploadedFile DB record.
        user_id: Owner of the file.

    Returns:
        dict with transactions_created count.
    """
    db = SessionLocal()
    try:
        uploaded_file = db.query(UploadedFile).filter(UploadedFile.id == uploaded_file_id).first()
        if not uploaded_file:
            return {"error": f"UploadedFile {uploaded_file_id} not found"}

        uploaded_file.status = "parsing"
        db.commit()

        file_path = uploaded_file.s3_key  # Local path or MinIO key

        if uploaded_file.file_type == "pdf":
            parsed_rows = parse_pdf(file_path)
        else:
            parsed_rows = parse_csv(file_path)

        created = normalization_service.normalize(
            db=db,
            user_id=user_id,
            parsed_rows=parsed_rows,
            source_type=uploaded_file.file_type,
            source_reference_id=uploaded_file_id,
        )

        uploaded_file.status = "completed"
        db.commit()

        return {"transactions_created": len(created), "file_id": uploaded_file_id}

    except Exception as e:
        if db:
            try:
                uploaded_file = db.query(UploadedFile).filter(UploadedFile.id == uploaded_file_id).first()
                if uploaded_file:
                    uploaded_file.status = "failed"
                    db.commit()
            except Exception:
                pass
        raise self.retry(exc=e, countdown=10, max_retries=2)
    finally:
        db.close()


@celery_app.task(bind=True, name="tasks.parse_sms_batch")
def parse_sms_batch_task(self, user_id: int):
    """
    Async task: parse all pending SMS RawRecords for a user.

    Returns:
        dict with transactions_created count.
    """
    db = SessionLocal()
    total_created = 0
    try:
        pending = db.query(RawRecord).filter(
            RawRecord.user_id == user_id,
            RawRecord.source_type == "sms",
            RawRecord.parsed_status == "pending",
        ).all()

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
        return {"transactions_created": total_created}
    except Exception as e:
        raise self.retry(exc=e, countdown=10, max_retries=2)
    finally:
        db.close()
