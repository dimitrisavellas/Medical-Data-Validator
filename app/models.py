from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime

class Base(DeclarativeBase):
    pass

class AuditLog(Base):
    __tablename__ = 'audit_log'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    details: Mapped[str] = mapped_column(Text)
    user: Mapped[str] = mapped_column(String(100), default='system')
    record_hash: Mapped[str] = mapped_column(String(64), nullable=True)  # SHA-256 hash
