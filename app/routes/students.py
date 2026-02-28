# from fastapi import APIRouter, Depends
# from sqlalchemy.orm import Session
# from typing import List
# from app.database import get_db
# from app.models import Student

# router = APIRouter(prefix="/students", tags=["Students"])

# @router.get("/", response_model=List[dict])
# def get_students(db: Session = Depends(get_db)):
#     students = db.query(Student).all()
#     return [
#         {
#             "student_id": student.student_id,
#             "student_number": student.student_number,
#             "name": student.name,
#             "major": student.major,
#             "level": student.level,
#             "image_path": student.image_path,
#             "created_at": student.created_at
#         }
#         for student in students
#     ]
# from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
# from sqlalchemy.orm import Session
# import face_recognition
# import numpy as np
# import os
# from datetime import datetime

# from app.database import get_db
# from app.models import Student

# router = APIRouter(prefix="/students", tags=["Students"])


# @router.post("/register-with-face")
# async def register_student_with_face(
#     student_number: str = Form(...),
#     name: str = Form(...),
#     major: str = Form(None),
#     level: str = Form(None),
#     image: UploadFile = File(...),
#     db: Session = Depends(get_db)
# ):
#     try:
#         os.makedirs("storage/students", exist_ok=True)

#         file_path = f"storage/students/{student_number}_{datetime.now().timestamp()}.jpg"

#         # حفظ الصورة
#         contents = await image.read()
#         with open(file_path, "wb") as f:
#             f.write(contents)

#         # ✅ الطريقة الصحيحة لتحميل الصورة
#         img = face_recognition.load_image_file(file_path)

#         print("Image Shape:", img.shape)
#         print("Image Dtype:", img.dtype)

#         # كشف الوجه
#         face_locations = face_recognition.face_locations(img)

#         if len(face_locations) == 0:
#             os.remove(file_path)
#             raise HTTPException(status_code=400, detail="لم يتم اكتشاف أي وجه في الصورة")

#         if len(face_locations) > 1:
#             os.remove(file_path)
#             raise HTTPException(status_code=400, detail="يوجد أكثر من وجه في الصورة")

#         # استخراج البصمة
#         face_encoding = face_recognition.face_encodings(
#             img,
#             known_face_locations=face_locations,
#             model="small"
#         )[0]

#         face_encoding_bytes = face_encoding.tobytes()

#         new_student = Student(
#             student_number=student_number,
#             name=name,
#             major=major,
#             level=level,
#             face_encoding=face_encoding_bytes,
#             image_path=file_path
#         )

#         db.add(new_student)
#         db.commit()
#         db.refresh(new_student)

#         return {
#             "message": "تم تسجيل الطالب مع بصمة الوجه بنجاح",
#             "student_id": new_student.student_id
#         }

#     except Exception as e:
#         print("REAL ERROR:", e)
#         raise
# ------------------------------------------------------------------------
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Student

from insightface.app import FaceAnalysis
import numpy as np
import cv2
import os
from datetime import datetime

router = APIRouter(prefix="/students", tags=["Students"])

# تحميل النموذج مرة واحدة فقط
app_face = FaceAnalysis(name="buffalo_l")
app_face.prepare(ctx_id=0)


@router.post("/register-with-face")
async def register_student_with_face(
    student_number: str = Form(...),
    name: str = Form(...),
    major: str = Form(None),
    level: str = Form(None),
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        # التحقق من عدم وجود الطالب مسبقاً
        existing = db.query(Student).filter(Student.student_number == student_number).first()
        if existing:
            raise HTTPException(status_code=400, detail="رقم الطالب موجود مسبقاً")

        os.makedirs("storage/students", exist_ok=True)

        file_path = f"storage/students/{student_number}_{datetime.now().timestamp()}.jpg"

        with open(file_path, "wb") as buffer:
            buffer.write(await image.read())

        img = cv2.imread(file_path)

        if img is None:
            os.remove(file_path)
            raise HTTPException(status_code=400, detail="فشل في قراءة الصورة")

        faces = app_face.get(img)

        if len(faces) == 0:
            os.remove(file_path)
            raise HTTPException(status_code=400, detail="لم يتم اكتشاف أي وجه")

        if len(faces) > 1:
            os.remove(file_path)
            raise HTTPException(status_code=400, detail="يوجد أكثر من وجه في الصورة")

        embedding = faces[0].embedding

        # تحويل إلى bytes
        embedding_bytes = embedding.astype(np.float32).tobytes()

        new_student = Student(
            student_number=student_number,
            name=name,
            major=major,
            level=level,
            face_embedding=embedding_bytes,
            image_path=file_path
        )

        db.add(new_student)
        db.commit()
        db.refresh(new_student)

        return {
            "message": "تم تسجيل الطالب بنجاح باستخدام ArcFace",
            "student_id": new_student.student_id
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))