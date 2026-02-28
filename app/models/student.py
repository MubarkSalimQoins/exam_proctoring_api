# from sqlalchemy import Column, Integer, String, LargeBinary, DateTime
# from app.database import Base

# class Student(Base):
#     __tablename__ = "students"
    
#     student_id = Column(Integer, primary_key=True, autoincrement=True)
#     student_number = Column(String(50), unique=True, nullable=False)
#     name = Column(String(255), nullable=False)
#     major = Column(String(100), nullable=False)
#     level = Column(String(50), nullable=False)
#     face_encoding = Column(LargeBinary, nullable=True)
#     image_path = Column(String(500), nullable=True)
#     created_at = Column(DateTime, nullable=False)
# ---------------------------------------------------------------------------------
from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.dialects.mysql import LONGBLOB
from app.database import Base
from sqlalchemy.sql import func

class Student(Base):
    __tablename__ = "students"   # ← التصحيح هنا

    student_id = Column(Integer, primary_key=True, index=True)
    student_number = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    major = Column(String(100))
    level = Column(String(50))
    face_embedding = Column(LONGBLOB, nullable=False)
    image_path = Column(String(255))