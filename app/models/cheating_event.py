from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from app.database import Base

class CheatingEvent(Base):
    __tablename__ = "cheating_events"
    
    event_id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.student_id"), nullable=False)
    cheating_type_id = Column(Integer, ForeignKey("cheating_types.cheating_type_id"), nullable=False)
    status = Column(String(20), nullable=False)
    confidence_score = Column(Float, nullable=False)
    snapshot_path = Column(String(500), nullable=True)
    video_path = Column(String(500), nullable=True)
    event_time = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False)