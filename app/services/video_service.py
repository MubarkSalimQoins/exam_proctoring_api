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
import cv2
import time

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

            if not self.identity_verified:

                if current_time - start_time <= 5:

                    result = self.face_service.identify_student(frame)

                    if result["match"]:

                        self.identity_verified = True
                        print(f"✅ تم التعرف على الطالب: {result['student_name']}")

                    else:
                        print("❌ هذا الشخص غير مسجل في النظام")

                else:

                    if not self.identity_verified:
                        print("❌ فشل التحقق من الهوية")
                        break

            cv2.imshow("Exam Monitoring", frame)

            if cv2.waitKey(1) & 0xFF == 27:
                break

        cap.release()
        cv2.destroyAllWindows()