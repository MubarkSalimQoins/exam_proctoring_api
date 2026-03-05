# from fastapi import APIRouter, UploadFile, File, HTTPException
# import numpy as np
# import cv2
# import insightface

# router = APIRouter(prefix="/face", tags=["Face"])

# تحميل الموديل مرة واحدة فقط
# app_face = insightface.app.FaceAnalysis(name="buffalo_l")
# app_face.prepare(ctx_id=-1)  # CPU

# @router.post("/extract-embedding")
# async def extract_embedding(image: UploadFile = File(...)):
#     try:
#         contents = await image.read()
#         npimg = np.frombuffer(contents, np.uint8)
#         img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

#         if img is None:
#             raise HTTPException(status_code=400, detail="Invalid image")

#         faces = app_face.get(img)

#         if len(faces) == 0:
#             raise HTTPException(status_code=400, detail="No face detected")

#         if len(faces) > 1:
#             raise HTTPException(status_code=400, detail="Multiple faces detected")

#         embedding = faces[0].embedding.tolist()

#         return {
#             "status": "success",
#             "embedding": embedding
#         }

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
# -----------------------------------------------------------------------
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from sqlalchemy.orm import Session
import numpy as np
import cv2
import insightface

from app.database import get_db
from app.models.student import Student

router = APIRouter(prefix="/face", tags=["Face"])

# تحميل موديل التعرف على الوجه مرة واحدة فقط
app_face = insightface.app.FaceAnalysis(name="buffalo_l")
app_face.prepare(ctx_id=-1)  # CPU


# ==========================================
# 1️⃣ استخراج Face Embedding فقط
# ==========================================
@router.post("/extract-embedding")
async def extract_embedding(image: UploadFile = File(...)):
    try:
        contents = await image.read()

        npimg = np.frombuffer(contents, np.uint8)

        img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image")

        faces = app_face.get(img)

        if len(faces) == 0:
            raise HTTPException(status_code=400, detail="No face detected")

        if len(faces) > 1:
            raise HTTPException(status_code=400, detail="Multiple faces detected")

        embedding = faces[0].embedding.tolist()

        return {
            "status": "success",
            "embedding": embedding
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================
# 2️⃣ التحقق من هوية الطالب
# ==========================================
@router.post("/verify")
async def verify_face(
    student_id: int = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:

        # قراءة الصورة الجديدة
        contents = await image.read()
        npimg = np.frombuffer(contents, np.uint8)

        img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image")

        faces = app_face.get(img)

        if len(faces) == 0:
            raise HTTPException(status_code=400, detail="No face detected")

        if len(faces) > 1:
            raise HTTPException(status_code=400, detail="Multiple faces detected")

        # استخراج embedding الجديد
        new_embedding = faces[0].embedding.astype(np.float32)

        # جلب الطالب من قاعدة البيانات
        student = db.query(Student).filter(Student.student_id == student_id).first()

        if not student:
            raise HTTPException(status_code=404, detail="Student not found")

        # تحويل BLOB إلى numpy array
        stored_embedding = np.frombuffer(student.face_embedding, dtype=np.float32)

        # حساب التشابه Cosine Similarity
        similarity = float(
            np.dot(new_embedding, stored_embedding) /
            (np.linalg.norm(new_embedding) * np.linalg.norm(stored_embedding))
        )

        threshold = 0.6

        # إذا كان نفس الشخص
        if similarity >= threshold:

            return {
                "status": "success",
                "match": True,
                "student_name": student.name,
                "similarity": similarity
            }

        # إذا كان شخص مختلف
        else:

            return {
                "status": "success",
                "match": False,
                "message": "لا يوجد تطابق",
                "similarity": similarity
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))