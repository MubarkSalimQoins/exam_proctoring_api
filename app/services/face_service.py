# import cv2
# import numpy as np
# import insightface
# from sqlalchemy.orm import Session

# from app.database import SessionLocal
# from app.models.student import Student

# class FaceService:
#     def __init__(self):
#         # تحميل موديل InsightFace مرة واحدة فقط
#         self.app = insightface.app.FaceAnalysis(name="buffalo_l")
#         self.app.prepare(ctx_id=-1)

#         # حد التشابه
#         self.threshold = 0.6


#     def verify_student(self, frame, student_id):

#         try:

#             # استخراج الوجه من الصورة
#             faces = self.app.get(frame)

#             if len(faces) == 0:
#                 return {
#                     "match": False,
#                     "message": "لا يوجد وجه"
#                 }

#             if len(faces) > 1:
#                 return {
#                     "match": False,
#                     "message": "يوجد أكثر من شخص"
#                 }

#             # embedding الجديد
#             new_embedding = faces[0].embedding.astype(np.float32)

#             # الاتصال بقاعدة البيانات
#             db: Session = SessionLocal()

#             student = db.query(Student).filter(Student.student_id == student_id).first()

#             if not student:
#                 db.close()
#                 return {
#                     "match": False,
#                     "message": "الطالب غير موجود"
#                 }

#             # تحويل embedding المخزن
#             stored_embedding = np.frombuffer(student.face_embedding, dtype=np.float32)

#             # حساب التشابه
#             similarity = float(
#                 np.dot(new_embedding, stored_embedding) /
#                 (np.linalg.norm(new_embedding) * np.linalg.norm(stored_embedding))
#             )

#             db.close()

#             # إذا كان نفس الشخص
#             if similarity >= self.threshold:

#                 return {
#                     "match": True,
#                     "student_name": student.name,
#                     "similarity": similarity
#                 }

#             # شخص مختلف
#             else:

#                 return {
#                     "match": False,
#                     "similarity": similarity
#                 }

#         except Exception as e:

#             return {
#                 "match": False,
#                 "error": str(e)
#             }
# ----------------------------------------------------------------------------
# import cv2
# import numpy as np
# import insightface
# from sqlalchemy.orm import Session

# from app.database import SessionLocal
# from app.models.student import Student


# class FaceService:

#     def __init__(self):
#         self.app = insightface.app.FaceAnalysis(name="buffalo_l")
#         self.app.prepare(ctx_id=-1)

#         self.threshold = 0.6


#     def identify_student(self, frame):

#         try:

#             faces = self.app.get(frame)

#             if len(faces) == 0:
#                 return {"match": False, "message": "لا يوجد وجه"}

#             if len(faces) > 1:
#                 return {"match": False, "message": "يوجد أكثر من شخص"}

#             new_embedding = faces[0].embedding.astype(np.float32)

#             db: Session = SessionLocal()

#             students = db.query(Student).all()

#             best_similarity = 0
#             best_student = None

#             for student in students:

#                 stored_embedding = np.frombuffer(student.face_embedding, dtype=np.float32)

#                 similarity = float(
#                     np.dot(new_embedding, stored_embedding) /
#                     (np.linalg.norm(new_embedding) * np.linalg.norm(stored_embedding))
#                 )

#                 if similarity > best_similarity:
#                     best_similarity = similarity
#                     best_student = student

#             db.close()

#             if best_similarity >= self.threshold:

#                 return {
#                     "match": True,
#                     "student_name": best_student.name,
#                     "student_id": best_student.student_id,
#                     "similarity": best_similarity
#                 }

#             else:

#                 return {
#                     "match": False,
#                     "message": "الوجه غير موجود في النظام"
#                 }

#         except Exception as e:

#             return {
#                 "match": False,
#                 "error": str(e)
#             }
# --------------------------------------------------------------
import cv2
import numpy as np
import insightface
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.student import Student


class FaceService:

    def __init__(self):

        self.app = insightface.app.FaceAnalysis(name="buffalo_l")
        self.app.prepare(ctx_id=-1)

        self.threshold = 0.6


    def identify_student(self, frame):

        try:

            faces = self.app.get(frame)

            if len(faces) == 0:
                return {"match": False, "message": "لا يوجد وجه"}

            if len(faces) > 1:
                return {"match": False, "message": "يوجد أكثر من شخص"}

            new_embedding = faces[0].embedding.astype(np.float32)

            db: Session = SessionLocal()

            students = db.query(Student).all()

            if len(students) == 0:
                db.close()
                return {"match": False, "message": "لا يوجد طلاب في النظام"}

            best_similarity = 0
            best_student = None

            for student in students:

                stored_embedding = np.frombuffer(student.face_embedding, dtype=np.float32)

                similarity = float(
                    np.dot(new_embedding, stored_embedding) /
                    (np.linalg.norm(new_embedding) * np.linalg.norm(stored_embedding))
                )

                if similarity > best_similarity:
                    best_similarity = similarity
                    best_student = student

            db.close()

            if best_similarity >= self.threshold:

                return {
                    "match": True,
                    "student_name": best_student.name,
                    "student_id": best_student.student_id,
                    "similarity": best_similarity
                }

            else:

                return {
                    "match": False,
                    "message": "شخص غير معروف"
                }

        except Exception as e:

            return {
                "match": False,
                "error": str(e)
            }