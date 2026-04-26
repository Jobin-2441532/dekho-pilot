from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    cta = Column(String)
    tag = Column(String) # e.g. "Save", "Invest"
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="recommendations")
