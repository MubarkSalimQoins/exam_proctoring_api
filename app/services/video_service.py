# import cv2
# import time
# import requests
# import os
# from collections import deque

# from app.services.face_service import FaceService
# from app.services.object_detection import ObjectDetectionService
# from app.services.head_pose_service import HeadPoseService
# from app.services.audio_service import AudioService
# from app.services.email_service import EmailService


# class VideoMonitoringService:

#     def __init__(self):

#         # الخدمات
#         self.face_service = FaceService()
#         self.object_detector = ObjectDetectionService()
#         self.head_pose_service = HeadPoseService()
#         self.audio_service = AudioService()
#         self.email_service = EmailService()

#         # بيانات الطالب
#         self.identity_verified = False
#         self.student_id = None
#         self.student_name = None

#         # منع تكرار نفس الغش
#         self.last_cheating_time = {}
#         self.cooldown = 5

#         # حفظ الفيديو قبل الغش
#         self.frame_buffer = deque(maxlen=150)

#         # مجلد الأدلة
#         self.evidence_dir = "evidence"

#         os.makedirs(self.evidence_dir, exist_ok=True)


#     def save_snapshot(self, frame):

#         timestamp = int(time.time())

#         path = f"{self.evidence_dir}/snapshot_{timestamp}.jpg"

#         cv2.imwrite(path, frame)

#         return path


#     def save_video_clip(self):

#         timestamp = int(time.time())

#         path = f"{self.evidence_dir}/video_{timestamp}.avi"

#         if len(self.frame_buffer) == 0:
#             return None

#         height, width, _ = self.frame_buffer[0].shape

#         fourcc = cv2.VideoWriter_fourcc(*"XVID")

#         out = cv2.VideoWriter(path, fourcc, 20.0, (width, height))

#         for f in self.frame_buffer:
#             out.write(f)

#         out.release()

#         return path


#     def send_cheating_event(self, cheating, frame):

#         cheating_type_id = cheating["cheating_type_id"]

#         current_time = time.time()

#         # منع تكرار نفس الحدث
#         if cheating_type_id in self.last_cheating_time:
#             if current_time - self.last_cheating_time[cheating_type_id] < self.cooldown:
#                 return

#         self.last_cheating_time[cheating_type_id] = current_time

#         try:

#             snapshot_path = self.save_snapshot(frame)

#             video_path = self.save_video_clip()

#             data = {
#                 "student_id": self.student_id,
#                 "cheating_type_id": cheating_type_id,
#                 "status": "suspected",
#                 "confidence_score": cheating["confidence"],
#                 "snapshot_path": snapshot_path,
#                 "video_path": video_path
#             }
            

#             # إرسال الحدث إلى API
#             requests.post(
#                 "http://127.0.0.1:8000/cheating-events/",
#                 json=data
#             )

#             print(f"🚨 حالة غش: {cheating['type_ar']}")

#             # إرسال الإيميل
#             self.email_service.send_cheating_alert(
#                 student_id=self.student_id,
#                 cheating_type=cheating["type_ar"],
#                 confidence=cheating["confidence"],
#                 snapshot_path=snapshot_path,
#                 video_path=video_path
#             )

#         except Exception as e:

#             print("خطأ إرسال الغش:", e)


#     def start_monitoring(self):

#         cap = cv2.VideoCapture(0)

#         if not cap.isOpened():

#             print("❌ لا يمكن فتح الكاميرا")

#             return

#         print("🎥 تم تشغيل الكاميرا")

#         # تشغيل مراقبة الصوت
#         self.audio_service.start()

#         start_time = time.time()

#         while True:

#             ret, frame = cap.read()

#             if not ret:
#                 break

#             # حفظ الفريم للفيديو
#             self.frame_buffer.append(frame.copy())

#             current_time = time.time()

#             # =================================
#             # التحقق من الطالب (5 ثواني)
#             # =================================

#             if not self.identity_verified:

#                 if current_time - start_time <= 10:

#                     result = self.face_service.identify_student(frame)

#                     if result["match"]:

#                         self.identity_verified = True
#                         self.student_id = result["student_id"]
#                         self.student_name = result["student_name"]

#                         print(f"✅ تم التعرف على الطالب: {self.student_name}")

#                 else:

#                     if not self.identity_verified:

#                         print("❌ فشل التحقق من الهوية")

#                         break

#             # =================================
#             # مراقبة الغش
#             # =================================

#             else:

#                 cheating_events = []

#                 # كشف الجوال والسماعات
#                 obj_cheating = self.object_detector.detect_cheating(frame)

#                 cheating_events.extend(obj_cheating)

#                 # كشف حركة الرأس
#                 head_cheating = self.head_pose_service.detect_head_pose(frame)

#                 if head_cheating:
#                     cheating_events.append(head_cheating)

#                 # كشف الصوت
#                 audio_cheating = self.audio_service.detect_noise()

#                 if audio_cheating:
#                     cheating_events.append(audio_cheating)

#                 # إرسال الحالات المكتشفة
#                 for cheating in cheating_events:

#                     self.send_cheating_event(cheating, frame)

#             cv2.imshow("Exam Monitoring", frame)

#             if cv2.waitKey(1) & 0xFF == 27:
#                 break

#         # إيقاف الصوت
#         self.audio_service.stop()

#         cap.release()

#         cv2.destroyAllWindows()

# --------------------------------------------------
# هذا يعتمد فيه الارسال 
# import cv2
# import time
# import requests
# import os
# import winsound
# from collections import deque

# from app.services.face_service import FaceService
# from app.services.object_detection import ObjectDetectionService
# from app.services.head_pose_service import HeadPoseService
# from app.services.audio_service import AudioService
# from app.services.email_service import EmailService


# class VideoMonitoringService:

#     def __init__(self):

#         # الخدمات
#         self.face_service = FaceService()
#         self.object_detector = ObjectDetectionService()
#         self.head_pose_service = HeadPoseService()
#         self.audio_service = AudioService()
#         self.email_service = EmailService()

#         # بيانات الطالب
#         self.identity_verified = False
#         self.student_id = None
#         self.student_name = None

#         # منع تكرار نفس الغش
#         self.last_cheating_time = {}
#         self.cooldown = 5

#         # حفظ الفيديو قبل الغش
#         self.frame_buffer = deque(maxlen=200)

#         # مجلد الأدلة
#         self.evidence_dir = "evidence"
#         os.makedirs(self.evidence_dir, exist_ok=True)

#         self.exam_started = False


#     def save_snapshot(self, frame):

#         timestamp = int(time.time())
#         path = f"{self.evidence_dir}/snapshot_{timestamp}.jpg"

#         cv2.imwrite(path, frame)

#         return path


#     def save_video_clip(self):

#         if len(self.frame_buffer) < 30:
#             return None

#         timestamp = int(time.time())

#         path = f"{self.evidence_dir}/video_{timestamp}.avi"

#         height, width, _ = self.frame_buffer[0].shape

#         fourcc = cv2.VideoWriter_fourcc(*"XVID")

#         out = cv2.VideoWriter(path, fourcc, 20.0, (width, height))

#         for f in self.frame_buffer:
#             out.write(f)

#         out.release()

#         return path


#     def play_alarm(self):

#         try:
#             winsound.Beep(2000, 700)
#         except:
#             pass


#     def send_cheating_event(self, cheating, frame):

#         cheating_type_id = cheating["cheating_type_id"]

#         current_time = time.time()

#         if cheating_type_id in self.last_cheating_time:
#             if current_time - self.last_cheating_time[cheating_type_id] < self.cooldown:
#                 return

#         self.last_cheating_time[cheating_type_id] = current_time

#         try:

#             snapshot_path = self.save_snapshot(frame)

#             video_path = self.save_video_clip()

#             data = {
#                 "student_id": self.student_id,
#                 "cheating_type_id": cheating_type_id,
#                 "status": "suspected",
#                 "confidence_score": cheating["confidence"],
#                 "snapshot_path": snapshot_path,
#                 "video_path": video_path
#             }

#             requests.post(
#                 "http://127.0.0.1:8000/cheating-events/",
#                 json=data
#             )

#             print(f"🚨 حالة غش: {cheating['type_ar']}")

#             # تشغيل صوت إنذار
#             self.play_alarm()

#             # إرسال الإيميل
#             self.email_service.send_cheating_alert(
#                 student_name=self.student_name,
#                 student_number=self.student_id,
#                 cheating_type=cheating["type_ar"],
#                 confidence=cheating["confidence"],
#                 snapshot_path=snapshot_path,
#                 video_path=video_path
#             )

#         except Exception as e:

#             print("خطأ إرسال الغش:", e)


#     def start_monitoring(self):

#         cap = cv2.VideoCapture(0)

#         if not cap.isOpened():

#             print("❌ لا يمكن فتح الكاميرا")

#             return

#         print("🎥 تم تشغيل الكاميرا")

#         self.audio_service.start()

#         start_time = time.time()

#         while True:

#             ret, frame = cap.read()

#             if not ret:
#                 break

#             self.frame_buffer.append(frame.copy())

#             current_time = time.time()

#             # =================================
#             # التحقق من الطالب
#             # =================================

#             if not self.identity_verified:

#                 if current_time - start_time <= 5:

#                     result = self.face_service.identify_student(frame)

#                     if result["match"]:

#                         self.identity_verified = True
#                         self.student_id = result["student_id"]
#                         self.student_name = result["student_name"]
#                         self.exam_started = True

#                         print(f"✅ تم التعرف على الطالب: {self.student_name}")

#                 else:

#                     if not self.identity_verified:

#                         cv2.putText(frame, "Identity Failed",
#                                     (50, 80),
#                                     cv2.FONT_HERSHEY_SIMPLEX,
#                                     1,
#                                     (0, 0, 255),
#                                     3)

#                         print("❌ فشل التحقق من الهوية")

#                         break

#             # =================================
#             # مراقبة الغش
#             # =================================

#             else:

#                 cv2.putText(frame,
#                             "Exam Started",
#                             (20, 40),
#                             cv2.FONT_HERSHEY_SIMPLEX,
#                             1,
#                             (0, 255, 0),
#                             3)

#                 cheating_events = []

#                 obj_cheating = self.object_detector.detect_cheating(frame)

#                 cheating_events.extend(obj_cheating)

#                 head_cheating = self.head_pose_service.detect_head_pose(frame)

#                 if head_cheating:
#                     cheating_events.append(head_cheating)

#                 audio_cheating = self.audio_service.detect_noise()

#                 if audio_cheating:
#                     cheating_events.append(audio_cheating)

#                 for cheating in cheating_events:

#                     self.send_cheating_event(cheating, frame)

#                     cv2.putText(frame,
#                                 f"Cheating: {cheating['type_ar']}",
#                                 (20, 80),
#                                 cv2.FONT_HERSHEY_SIMPLEX,
#                                 1,
#                                 (0, 0, 255),
#                                 3)

#             cv2.imshow("Exam Monitoring", frame)

#             if cv2.waitKey(1) & 0xFF == 27:
#                 break

#         self.audio_service.stop()

#         cap.release()

#         cv2.destroyAllWindows()
    # -------------------------------------------------
import cv2
import time
import requests
import os
import winsound
from collections import deque

from app.services.face_service import FaceService
from app.services.object_detection import ObjectDetectionService
from app.services.head_pose_service import HeadPoseService
from app.services.audio_service import AudioService
from app.services.email_service import EmailService


class VideoMonitoringService:

    def __init__(self):

        # الخدمات
        self.face_service = FaceService()
        self.object_detector = ObjectDetectionService()
        self.head_pose_service = HeadPoseService()
        self.audio_service = AudioService()
        self.email_service = EmailService()

        # بيانات الطالب
        self.identity_verified = False
        self.student_id = None
        self.student_name = None

        # منع التكرار
        self.last_cheating_time = {}
        self.cooldown = 5

        # 5 ثواني قبل الغش (100 فريم)
        self.frame_buffer = deque(maxlen=100)

        # مجلد الأدلة
        self.evidence_dir = "evidence"
        os.makedirs(self.evidence_dir, exist_ok=True)

        self.exam_started = False


    def save_snapshot(self, frame):

        timestamp = int(time.time())

        path = f"{self.evidence_dir}/snapshot_{timestamp}.jpg"

        cv2.imwrite(path, frame)

        print(f"📸 تم حفظ الصورة: {path}")

        return path


    def save_video_clip(self, cap):

        if len(self.frame_buffer) == 0:

            print("⚠ لا يوجد فريمات قبل الغش")

            return None

        timestamp = int(time.time())

        path = f"{self.evidence_dir}/video_{timestamp}.mp4"

        height, width, _ = self.frame_buffer[0].shape

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")

        out = cv2.VideoWriter(path, fourcc, 20.0, (width, height))

        if not out.isOpened():

            print("❌ فشل إنشاء ملف الفيديو")

            return None

        frame_count = 0

        # حفظ 5 ثواني قبل الغش
        for f in self.frame_buffer:

            out.write(f)

            frame_count += 1

        print("🎥 تم حفظ الفيديو قبل الغش")

        # تسجيل 5 ثواني بعد الغش
        for i in range(100):

            ret, frame = cap.read()

            if not ret:
                break

            out.write(frame)

            frame_count += 1

        out.release()

        print(f"🎬 تم حفظ الفيديو: {path}")

        print(f"📊 عدد الفريمات: {frame_count}")

        return path


    def play_alarm(self):

        try:

            winsound.Beep(2000, 700)

        except:

            pass


    def send_cheating_event(self, cheating, frame, cap):

        cheating_type_id = cheating["cheating_type_id"]

        current_time = time.time()

        if cheating_type_id in self.last_cheating_time:

            if current_time - self.last_cheating_time[cheating_type_id] < self.cooldown:

                return

        self.last_cheating_time[cheating_type_id] = current_time

        try:

            snapshot_path = self.save_snapshot(frame)

            video_path = self.save_video_clip(cap)

            data = {
                "student_id": self.student_id,
                "cheating_type_id": cheating_type_id,
                "status": "suspected",
                "confidence_score": cheating["confidence"],
                "snapshot_path": snapshot_path,
                "video_path": video_path
            }

            requests.post(
                "http://127.0.0.1:8000/cheating-events/",
                json=data
            )

            print(f"🚨 حالة غش: {cheating['type_ar']}")

            self.play_alarm()

            # إرسال الإيميل
            self.email_service.send_cheating_alert(
                student_name=self.student_name,
                student_number=self.student_id,
                cheating_type=cheating["type_ar"],
                confidence=cheating["confidence"],
                snapshot_path=snapshot_path,
                video_path=video_path
            )

            print("📧 تم إرسال الإيميل")

        except Exception as e:

            print("❌ خطأ إرسال الغش:", e)


    def start_monitoring(self):

        cap = cv2.VideoCapture(0)

        if not cap.isOpened():

            print("❌ لا يمكن فتح الكاميرا")

            return

        print("🎥 تم تشغيل الكاميرا")

        self.audio_service.start()

        start_time = time.time()

        while True:

            ret, frame = cap.read()

            if not ret:

                break

            # حفظ الفريمات في البفر دائماً
            self.frame_buffer.append(frame.copy())

            current_time = time.time()

            # التحقق من الهوية
            if not self.identity_verified:

                if current_time - start_time <= 5:

                    result = self.face_service.identify_student(frame)

                    if result["match"]:

                        self.identity_verified = True
                        self.student_id = result["student_id"]
                        self.student_name = result["student_name"]
                        self.exam_started = True

                        print(f"✅ تم التعرف على الطالب: {self.student_name}")

                else:

                    if not self.identity_verified:

                        print("❌ فشل التحقق من الهوية")

                        break

            else:

                cv2.putText(frame,
                            "Exam Started",
                            (20, 40),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1,
                            (0, 255, 0),
                            3)

                cheating_events = []

                obj_cheating = self.object_detector.detect_cheating(frame)

                cheating_events.extend(obj_cheating)

                head_cheating = self.head_pose_service.detect_head_pose(frame)

                if head_cheating:

                    cheating_events.append(head_cheating)

                audio_cheating = self.audio_service.detect_noise()

                if audio_cheating:

                    cheating_events.append(audio_cheating)

                for cheating in cheating_events:

                    self.send_cheating_event(cheating, frame, cap)

                    cv2.putText(frame,
                                f"Cheating: {cheating['type_ar']}",
                                (20, 80),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                1,
                                (0, 0, 255),
                                3)

            cv2.imshow("Exam Monitoring", frame)

            if cv2.waitKey(1) & 0xFF == 27:

                break

        self.audio_service.stop()

        cap.release()

        cv2.destroyAllWindows()
        