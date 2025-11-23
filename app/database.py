from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class AuditLog(Base):
    """SQLite audit trail table"""
    __tablename__ = 'audit_log'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.now)
    action = Column(String(50), nullable=False)
    details = Column(Text)
    user = Column(String(100), default='system')
    record_hash = Column(String(64))  # For data integrity verification

class AuditDatabase:
    def __init__(self, db_path='sqlite:////logs/audit_trail.db'):
        self.engine = create_engine(db_path)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    
    def log_action(self, action: str, details: str, user: str = 'system'):
        """Add entry to audit database"""
        entry = AuditLog(
            action=action,
            details=details,
            user=user,
            timestamp=datetime.now()
        )
        self.session.add(entry)
        self.session.commit()
        return entry.id
    
    def get_audit_trail(self):
        """Retrieve complete audit trail"""
        return self.session.query(AuditLog).all()
    
    def close(self):
        self.session.close()
