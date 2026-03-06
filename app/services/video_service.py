# import cv2
# import time

# from app.services.face_service import FaceService
# from app.services.object_detection import ObjectDetectionService
# from app.services.head_pose_service import HeadPoseService
# from app.services.audio_service import AudioService


# class VideoMonitoringService:

#     def __init__(self):  # <- هذا الصحيح
#         self.face_service = FaceService()
#         self.object_detector = ObjectDetectionService()
#         self.head_pose_service = HeadPoseService()
#         self.audio_service = AudioService()
#         self.identity_verified = False

#     def start_monitoring(self, student_id):

#         cap = cv2.VideoCapture(0)

#         if not cap.isOpened():
#             print("❌ لا يمكن فتح الكاميرا")
#             return

#         print("🎥 تم تشغيل الكاميرا")

#         start_time = time.time()

#         while True:

#             ret, frame = cap.read()

#             if not ret:
#                 break

#             current_time = time.time()

#             # =============================
#             # أول 5 ثواني للتحقق من الوجه
#             # =============================
#             if not self.identity_verified:

#                 if current_time - start_time <= 5:

#                     result = self.face_service.verify_student(frame, student_id)

#                     if result["match"]:

#                         self.identity_verified = True
#                         print(f"✅ تم التحقق من الطالب: {result['student_name']}")

#                     else:
#                         print("❌ الوجه غير مطابق للطالب")

#                 else:

#                     if not self.identity_verified:
#                         print("❌ فشل التحقق من هوية الطالب")
#                         break

#             else:

#                 # =============================
#                 # اكتشاف الأشياء (جوال / سماعات)
#                 # =============================
#                 object_cheating = self.object_detector.detect_cheating(frame)

#                 if object_cheating:
#                     print("🚨 غش مكتشف:", object_cheating)

#                 # =============================
#                 # اكتشاف حركة الرأس
#                 # =============================
#                 head_cheating = self.head_pose_service.detect_head_movement(frame)

#                 if head_cheating:
#                     print("🚨 حركة رأس مشبوهة")

#                 # =============================
#                 # اكتشاف الصوت
#                 # =============================
#                 audio_cheating = self.audio_service.detect_noise()

#                 if audio_cheating:
#                     print("🚨 صوت مرتفع")

#             cv2.imshow("Exam Monitoring", frame)

#             if cv2.waitKey(1) & 0xFF == 27:
#                 break

#         cap.release()
#         cv2.destroyAllWindows()
# -------------------------------------------------------
# هذا الكود افضل من الاول
# import cv2
# import time

# from app.services.face_service import FaceService
# from app.services.object_detection import ObjectDetectionService
# from app.services.head_pose_service import HeadPoseService
# from app.services.audio_service import AudioService


# class VideoMonitoringService:

#     def __init__(self):
#         self.face_service = FaceService()
#         self.object_detector = ObjectDetectionService()
#         self.head_pose_service = HeadPoseService()
#         self.audio_service = AudioService()
#         self.identity_verified = False

#     def start_monitoring(self):

#         cap = cv2.VideoCapture(0)

#         if not cap.isOpened():
#             print("❌ لا يمكن فتح الكاميرا")
#             return

#         print("🎥 تم تشغيل الكاميرا")

#         start_time = time.time()

#         while True:

#             ret, frame = cap.read()

#             if not ret:
#                 break

#             current_time = time.time()

#             if not self.identity_verified:

#                 if current_time - start_time <= 5:

#                     result = self.face_service.identify_student(frame)

#                     if result["match"]:

#                         self.identity_verified = True
#                         print(f"✅ تم التعرف على الطالب: {result['student_name']}")
#                         print(f"✅ تم التعرف على الطالب: {result['student_id']}")

#                     else:
#                         print("❌ هذا الشخص غير مسجل في النظام")

#                 else:

#                     if not self.identity_verified:
#                         print("❌ فشل التحقق من الهوية")
#                         break

#             cv2.imshow("Exam Monitoring", frame)

#             if cv2.waitKey(1) & 0xFF == 27:
#                 break

#         cap.release()
#         cv2.destroyAllWindows()
        
# --------------------------------------------
import cv2
import time
import requests

from app.services.face_service import FaceService
from app.services.object_detection import ObjectDetectionService
from app.services.head_pose_service import HeadPoseService
from app.services.audio_service import AudioService


class VideoMonitoringService:

    def __init__(self):

        self.face_service = FaceService()
        self.object_detector = ObjectDetectionService()
        self.head_pose_service = HeadPoseService()
        self.audio_service = AudioService()

        self.identity_verified = False
        self.student_id = None
        self.student_name = None

    def send_cheating_event(self, cheating):

        try:

            data = {
                "student_id": self.student_id,
                "cheating_type_id": cheating["type_id"],
                "status": "suspected",
                "confidence_score": cheating["confidence"],
                "snapshot_path": None,
                "video_path": None
            }

            requests.post(
                "http://127.0.0.1:8000/cheating-events/",
                json=data
            )

            print(f"🚨 تم تسجيل حالة غش: {cheating['type_ar']}")

        except Exception as e:
            print("خطأ إرسال الغش:", e)

    def start_monitoring(self):

        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            print("❌ لا يمكن فتح الكاميرا")
            return

        print("🎥 تم تشغيل الكاميرا")

        start_time = time.time()

        while True:

            ret, frame = cap.read()

            if not ret:
                break

            current_time = time.time()

            # =================================
            # مرحلة التحقق من الطالب (5 ثواني)
            # =================================
            if not self.identity_verified:

                if current_time - start_time <= 5:

                    result = self.face_service.identify_student(frame)

                    if result["match"]:

                        self.identity_verified = True
                        self.student_id = result["student_id"]
                        self.student_name = result["student_name"]

                        print(f"✅ تم التعرف على الطالب: {self.student_name}")

                    else:
                        print("❌ هذا الشخص غير مسجل")

                else:

                    if not self.identity_verified:
                        print("❌ فشل التحقق من الهوية")
                        break

            # =================================
            # مرحلة مراقبة الغش
            # =================================
            else:

                cheating_events = []

                # كشف الأشياء
                obj_cheating = self.object_detector.detect_cheating(frame)
                cheating_events.extend(obj_cheating)

                # كشف حركة الرأس
                head_cheating = self.head_pose_service.detect_head_pose(frame)
                if head_cheating:
                    cheating_events.append(head_cheating)

                # كشف الصوت
                audio_cheating = self.audio_service.detect_noise()
                if audio_cheating:
                    cheating_events.append(audio_cheating)

                # إرسال حالات الغش
                for cheating in cheating_events:
                    self.send_cheating_event(cheating)

            cv2.imshow("Exam Monitoring", frame)

            if cv2.waitKey(1) & 0xFF == 27:
                break

        cap.release()
        cv2.destroyAllWindows()