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
                return {"match": False, "message": "لا يوجد وجه", "students": []}

            db: Session = SessionLocal()
            students = db.query(Student).all()

            if len(students) == 0:
                db.close()
                return {"match": False, "message": "لا يوجد طلاب في النظام", "students": []}

            identified_students = []
            unknown_faces = []

            for face in faces:
                new_embedding = face.embedding.astype(np.float32)

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

                if best_similarity >= self.threshold:
                    identified_students.append({
                        "student_id": best_student.student_id,
                        "student_name": best_student.name,
                        "similarity": best_similarity,
                        "embedding": face.embedding.astype(np.float32).tobytes()  # تخزين الـ embedding
                    })
                else:
                    unknown_faces.append({
                        "similarity": best_similarity
                    })

            db.close()

            if len(unknown_faces) > 0:
                # يوجد أشخاص غير معروفين
                return {
                    "match": False,
                    "message": f"يوجد {len(unknown_faces)} شخص غير معروف",
                    "students": identified_students,
                    "unknown_count": len(unknown_faces)
                }

            if len(identified_students) == 0:
                return {
                    "match": False,
                    "message": "لا يوجد طلاب معروفين",
                    "students": [],
                    "unknown_count": 0
                }

            return {
                "match": True,
                "students": identified_students,
                "message": f"تم التعرف على {len(identified_students)} طلاب"
            }

        except Exception as e:

            return {
                "match": False,
                "error": str(e),
                "students": []
            }
            
            
# --------------------------------------------------------------
# هذا حق التحقق من طالب واحد 
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

#             if len(students) == 0:
#                 db.close()
#                 return {"match": False, "message": "لا يوجد طلاب في النظام"}

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
#                     "message": "شخص غير معروف"
#                 }

#         except Exception as e:

#             return {
#                 "match": False,
#                 "error": str(e)
#             }
            