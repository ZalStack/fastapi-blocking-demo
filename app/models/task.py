from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.sql import func
from app.database import Base

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String(255), nullable=False)
    status = Column(Enum('pending', 'processing', 'completed', 'failed'), default='pending')
    created_at = Column(DateTime, server_default=func.now())
completed_at = Column(DateTime, nullable=True)