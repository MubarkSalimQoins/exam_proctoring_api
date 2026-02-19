from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Student

router = APIRouter(prefix="/students", tags=["Students"])

@router.get("/", response_model=List[dict])
def get_students(db: Session = Depends(get_db)):
    students = db.query(Student).all()
    return [
        {
            "student_id": student.student_id,
            "student_number": student.student_number,
            "name": student.name,
            "major": student.major,
            "level": student.level,
            "image_path": student.image_path,
            "created_at": student.created_at
        }
        for student in students
    ]