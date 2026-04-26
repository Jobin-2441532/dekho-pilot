from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(String, nullable=False)
    merchant = Column(String)
    amount = Column(Float, nullable=False)
    category = Column(String)
    
    direction = Column(String) # credit/debit
    payment_mode = Column(String)
    source_type = Column(String) # pdf, csv, sms
    source_reference_id = Column(Integer, nullable=True)
    
    notes = Column(String)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="transactions")
