from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    filename = Column(String, nullable=False)
    file_size = Column(Integer)
    file_type = Column(String)
    storage_path = Column(String)
    status = Column(String, default="uploaded") # uploaded, processing, completed, failed
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="uploaded_files")

class RawRecord(Base):
    __tablename__ = "raw_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    file_id = Column(Integer, ForeignKey("uploaded_files.id"), nullable=True)
    raw_text = Column(String, nullable=False)
    source_type = Column(String) # sms, pdf, csv
    created_at = Column(DateTime, server_default=func.now())
