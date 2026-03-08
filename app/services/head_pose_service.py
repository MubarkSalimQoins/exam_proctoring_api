# class HeadPoseService:
#     def __init__(self):
#         pass

#     def detect_head_pose(self, frame):  # <-- غيرت الاسم هنا
#         # مؤقتاً نرجع False
#         return False
import cv2
import numpy as np
import insightface


class HeadPoseService:

    def __init__(self):

        # تحميل موديل الوجه
        self.app = insightface.app.FaceAnalysis(name="buffalo_l")
        self.app.prepare(ctx_id=-1)

        # حدود الحركة
        self.yaw_threshold = 30
        self.pitch_threshold = 25

    def detect_head_pose(self, frame):

        try:

            faces = self.app.get(frame)

            # إذا لم يوجد وجه
            if len(faces) == 0:

                return {
                    "cheating_type_id": 7,
                    "type_ar": "محاولة مغادرة الكاميرا",
                    "type_en": "Leaving Camera",
                    "confidence": 0.9
                }

            face = faces[0]

            # زوايا الرأس
            yaw = face.pose[0]
            pitch = face.pose[1]
            roll = face.pose[2]

            # النظر بعيد عن الشاشة
            if abs(yaw) > self.yaw_threshold:

                return {
                    "cheating_type_id": 4,
                    "type_ar": "النظر بعيداً عن الشاشة",
                    "type_en": "Looking Away",
                    "confidence": abs(yaw) / 90
                }

            # حركة رأس غير طبيعية
            if abs(pitch) > self.pitch_threshold:

                return {
                    "cheating_type_id": 5,
                    "type_ar": "حركة رأس غير طبيعية",
                    "type_en": "Abnormal Head Movement",
                    "confidence": abs(pitch) / 90
                }

            return None

        except Exception as e:

            print("Head Pose Error:", e)

            return None