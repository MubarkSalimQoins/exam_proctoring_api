from sqlalchemy import Column, Integer, String, Text
from app.database import Base

class CheatingType(Base):
    __tablename__ = "cheating_types"
    
    cheating_type_id = Column(Integer, primary_key=True)
    type_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)