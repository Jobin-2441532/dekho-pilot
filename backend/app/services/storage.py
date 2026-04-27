"""
FileStorageService — wraps MinIO object storage for all file operations.

Storage path convention:
  user_{user_id}/uploads/{file_id}.{ext}

All public file access goes through signed URLs with expiry — raw MinIO
paths are never exposed to API consumers.
"""
from __future__ import annotations

import os
from datetime import timedelta
from pathlib import Path
from typing import Optional

from minio import Minio
from minio.error import S3Error

# ---------------------------------------------------------------------------
# Config (read from env; defaults to local Docker MinIO)
# ---------------------------------------------------------------------------
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "dekho_minio")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "dekho_minio_password")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "dekho-uploads")
MINIO_SECURE = os.getenv("MINIO_SECURE", "false").lower() == "true"


class FileStorageService:
    """Handles upload/download/delete operations against a MinIO bucket."""

    def __init__(self):
        self._client: Optional[Minio] = None
        self._bucket = MINIO_BUCKET

    # ------------------------------------------------------------------
    # Lazy-initialise client (avoids crash at import time if MinIO is down)
    # ------------------------------------------------------------------
    @property
    def client(self) -> Minio:
        if self._client is None:
            self._client = Minio(
                MINIO_ENDPOINT,
                access_key=MINIO_ACCESS_KEY,
                secret_key=MINIO_SECRET_KEY,
                secure=MINIO_SECURE,
            )
            self._ensure_bucket()
        return self._client

    def _ensure_bucket(self):
        """Create the default bucket if it doesn't exist."""
        try:
            if not self._client.bucket_exists(self._bucket):
                self._client.make_bucket(self._bucket)
                print(f"✅ MinIO: Created bucket '{self._bucket}'")
        except S3Error as e:
            print(f"⚠️  MinIO: Could not ensure bucket — {e}")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def upload_file(
        self,
        user_id: int,
        file_id: str,
        local_path: str | Path,
        content_type: str = "application/octet-stream",
    ) -> str:
        """
        Upload a local file to MinIO and return its object key.

        Args:
            user_id:      Owner of the file.
            file_id:      Unique UUID for this upload.
            local_path:   Path to the file on disk.
            content_type: MIME type (e.g. "application/pdf").

        Returns:
            object_key: The MinIO key (e.g. "user_1/uploads/abc123.pdf")
        """
        local_path = Path(local_path)
        ext = local_path.suffix
        object_key = f"user_{user_id}/uploads/{file_id}{ext}"

        self.client.fput_object(
            bucket_name=self._bucket,
            object_name=object_key,
            file_path=str(local_path),
            content_type=content_type,
        )
        return object_key

    def get_signed_url(self, object_key: str, expires_hours: int = 1) -> str:
        """
        Generate a pre-signed temporary download URL.

        Args:
            object_key:    The MinIO object key (returned by upload_file).
            expires_hours: How many hours until the URL expires (default 1h).

        Returns:
            A time-limited HTTPS/HTTP URL.
        """
        url = self.client.presigned_get_object(
            bucket_name=self._bucket,
            object_name=object_key,
            expires=timedelta(hours=expires_hours),
        )
        return url

    def delete_file(self, object_key: str) -> bool:
        """
        Delete a file from MinIO.

        Returns:
            True on success, False if file not found or error.
        """
        try:
            self.client.remove_object(self._bucket, object_key)
            return True
        except S3Error as e:
            print(f"⚠️  MinIO delete failed for '{object_key}': {e}")
            return False

    def is_available(self) -> bool:
        """Health-check: returns True if MinIO is reachable."""
        try:
            _ = self.client  # triggers connection + bucket check
            return True
        except Exception:
            return False


# Singleton
storage_service = FileStorageService()
