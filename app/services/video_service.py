# --------------------------------
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

#         # منع التكرار
#         self.last_cheating_time = {}
#         self.cooldown = 5

#         # حفظ 5 ثواني قبل الغش (100 فريم)
#         self.frame_buffer = deque(maxlen=100)

#         # مجلد الأدلة داخل الموقع
#         self.evidence_dir = "C:/xampp/htdocs/exam_monitoring2/evidence"
#         os.makedirs(self.evidence_dir, exist_ok=True)

#         self.exam_started = False

#     # =========================
#     # حفظ صورة
#     # =========================
#     def save_snapshot(self, frame):
#         timestamp = int(time.time())
#         filename = f"snapshot_{timestamp}.jpg"
#         full_path = os.path.join(self.evidence_dir, filename)
#         cv2.imwrite(full_path, frame)
#         print(f"📸 تم حفظ الصورة: {full_path}")
#         return full_path, "evidence/" + filename

#     # =========================
#     # حفظ فيديو MP4
#     # =========================
#     def save_video_clip(self, cap):
#         if len(self.frame_buffer) == 0:
#             print("⚠ لا يوجد فريمات قبل الغش")
#             return None, None

#         timestamp = int(time.time())
#         filename = f"video_{timestamp}.mp4"
#         full_path = os.path.join(self.evidence_dir, filename)

#         height, width, _ = self.frame_buffer[0].shape

#         fourcc = cv2.VideoWriter_fourcc(*"mp4v")
#         out = cv2.VideoWriter(full_path, fourcc, 20.0, (width, height))

#         if not out.isOpened():
#             print("❌ فشل إنشاء الفيديو")
#             return None, None

#         frame_count = 0

#         # حفظ قبل الغش
#         for f in self.frame_buffer:
#             out.write(f)
#             frame_count += 1
#         print("🎥 تم حفظ الفيديو قبل الغش")

#         # حفظ بعد الغش (5 ثواني تقريبًا)
#         for i in range(100):
#             ret, frame = cap.read()
#             if not ret:
#                 print("⚠ فشل قراءة فريم بعد الغش")
#                 break
#             out.write(frame)
#             frame_count += 1

#         out.release()

#         # تحقق من الملف
#         if not os.path.exists(full_path) or os.path.getsize(full_path) == 0:
#             print("❌ الفيديو فارغ")
#             return None, None

#         print(f"🎬 تم حفظ الفيديو: {full_path}")
#         print(f"📊 عدد الفريمات: {frame_count}")

#         return full_path, "evidence/" + filename

#     # =========================
#     # إنذار صوتي
#     # =========================
#     def play_alarm(self):
#         try:
#             winsound.Beep(2000, 700)
#         except:
#             pass

#     # =========================
#     # إرسال حالة غش
#     # =========================
#     def send_cheating_event(self, cheating, frame, cap):
#         cheating_type_id = cheating["cheating_type_id"]
#         current_time = time.time()

#         if cheating_type_id in self.last_cheating_time:
#             if current_time - self.last_cheating_time[cheating_type_id] < self.cooldown:
#                 return

#         self.last_cheating_time[cheating_type_id] = current_time

#         try:
#             snapshot_full, snapshot_relative = self.save_snapshot(frame)
#             video_full, video_relative = self.save_video_clip(cap)

#             if video_relative:
#                 print(f"🎬 الفيديو جاهز للعرض: {video_relative}")
#             else:
#                 print("⚠ لن يتم إرسال فيديو")

#             data = {
#                 "student_id": self.student_id,
#                 "cheating_type_id": cheating_type_id,
#                 "status": "suspected",
#                 "confidence_score": cheating["confidence"],
#                 "snapshot_path": snapshot_relative,
#                 "video_path": video_relative if video_relative else None
#             }

#             print("📡 جاري الإرسال للسيرفر...")
#             print(data)

#             response = requests.post(
#                 "http://127.0.0.1:8000/cheating-events/",
#                 json=data
#             )
#             print(f"📥 رد السيرفر: {response.status_code}")
#             print(f"🚨 حالة غش: {cheating['type_ar']}")

#             self.play_alarm()

#             # إرسال إيميل
#             self.email_service.send_cheating_alert(
#                 student_name=self.student_name,
#                 student_number=self.student_id,
#                 cheating_type=cheating["type_ar"],
#                 confidence=cheating["confidence"],
#                 snapshot_path=snapshot_full,
#                 video_path=video_full
#             )

#             print("📧 تم إرسال الإيميل")

#         except Exception as e:
#             print("❌ خطأ:", e)

#     # =========================
#     # تشغيل النظام
#     # =========================
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

#             # التحقق من الهوية
#             if not self.identity_verified:
#                 if time.time() - start_time <= 5:
#                     result = self.face_service.identify_student(frame)
#                     if result["match"]:
#                         self.identity_verified = True
#                         self.student_id = result["student_id"]
#                         self.student_name = result["student_name"]
#                         print(f"✅ تم التعرف على الطالب: {self.student_name}")
#                 else:
#                     print("❌ فشل التحقق من الهوية")
#                     break
#             else:
#                 cv2.putText(frame, "Exam Started", (20, 40),
#                             cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)

#                 cheating_events = []
#                 cheating_events.extend(self.object_detector.detect_cheating(frame))

#                 head = self.head_pose_service.detect_head_pose(frame)
#                 if head:
#                     cheating_events.append(head)

#                 audio = self.audio_service.detect_noise()
#                 if audio:
#                     cheating_events.append(audio)

#                 for cheating in cheating_events:
#                     self.send_cheating_event(cheating, frame, cap)
#                     cv2.putText(frame, f"Cheating: {cheating['type_ar']}",
#                                 (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

#             cv2.imshow("Exam Monitoring", frame)

#             if cv2.waitKey(1) & 0xFF == 27:  # ESC للخروج
#                 break

#         self.audio_service.stop()
#         cap.release()
#         cv2.destroyAllWindows()
# --------------------------
# import cv2
# import time
# import requests
# import os
# import subprocess
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

#         # منع التكرار
#         self.last_cheating_time = {}
#         self.cooldown = 5

#         # سيتم تعيين maxlen لاحقاً بعد معرفة FPS الكاميرا
#         self.frame_buffer = deque()

#         # مجلد الأدلة داخل الموقع
#         self.evidence_dir = "C:/xampp/htdocs/exam_monitoring2/evidence"
#         os.makedirs(self.evidence_dir, exist_ok=True)

#         self.exam_started = False

#     # =========================
#     # حفظ صورة
#     # =========================
#     def save_snapshot(self, frame):
#         timestamp = int(time.time())
#         filename = f"snapshot_{timestamp}.jpg"
#         full_path = os.path.join(self.evidence_dir, filename)
#         cv2.imwrite(full_path, frame)
#         print(f"📸 تم حفظ الصورة: {full_path}")
#         return full_path, "evidence/" + filename

#     # =========================
#     # تحويل الفيديو لـ H.264
#     # =========================
#     def _convert_to_h264(self, input_path, output_path):
#         try:
#             cmd = [
#                 "ffmpeg",
#                 "-y",
#                 "-i", input_path,
#                 "-c:v", "libx264",
#                 "-preset", "fast",
#                 "-crf", "23",
#                 "-pix_fmt", "yuv420p",
#                 "-movflags", "+faststart",
#                 "-an",
#                 output_path
#             ]
#             result = subprocess.run(
#                 cmd,
#                 stdout=subprocess.PIPE,
#                 stderr=subprocess.PIPE,
#                 timeout=60
#             )
#             if result.returncode != 0:
#                 print("❌ FFmpeg error:", result.stderr.decode())
#                 return False
#             print("✅ تم التحويل لـ H.264 بنجاح")
#             return True
#         except FileNotFoundError:
#             print("❌ FFmpeg غير مثبت — شغّل: winget install ffmpeg")
#             return False
#         except subprocess.TimeoutExpired:
#             print("❌ FFmpeg استغرق وقتاً طويلاً")
#             return False

#     # =========================
#     # حفظ فيديو MP4
#     # =========================
#     def save_video_clip(self, cap):
#         if len(self.frame_buffer) == 0:
#             print("⚠ لا يوجد فريمات قبل الغش")
#             return None, None

#         timestamp = int(time.time())
#         temp_filename = f"temp_{timestamp}.avi"
#         final_filename = f"video_{timestamp}.mp4"
#         temp_path = os.path.join(self.evidence_dir, temp_filename)
#         full_path = os.path.join(self.evidence_dir, final_filename)

#         height, width, _ = self.frame_buffer[0].shape

#         # MJPG في AVI — مدعوم دائماً في OpenCV على Windows
#         fourcc = cv2.VideoWriter_fourcc(*"MJPG")
#         out = cv2.VideoWriter(temp_path, fourcc, 20.0, (width, height))

#         if not out.isOpened():
#             print("❌ فشل إنشاء الفيديو المؤقت")
#             return None, None

#         frame_count = 0

#         # حفظ فريمات قبل الغش
#         for f in self.frame_buffer:
#             out.write(f)
#             frame_count += 1
#         print("🎥 تم حفظ الفريمات قبل الغش")

#         # حفظ فريمات بعد الغش (~7 ثواني)
#         fps = cap.get(cv2.CAP_PROP_FPS) or 20
#         frames_after = int(fps * 7)  # 7 ثواني بعد الغش
#         for i in range(frames_after):
#             ret, frame = cap.read()
#             if not ret:
#                 print("⚠ فشل قراءة فريم بعد الغش")
#                 break
#             out.write(frame)
#             frame_count += 1

#         out.release()
#         print(f"📊 عدد الفريمات: {frame_count}")

#         # تحويل لـ H.264 متوافق مع المتصفحات
#         success = self._convert_to_h264(temp_path, full_path)

#         # حذف الملف المؤقت
#         if os.path.exists(temp_path):
#             os.remove(temp_path)

#         if not success:
#             return None, None

#         # تحقق من الملف النهائي
#         if not os.path.exists(full_path) or os.path.getsize(full_path) == 0:
#             print("❌ الفيديو النهائي فارغ")
#             return None, None

#         print(f"🎬 تم حفظ الفيديو: {full_path}")
#         return full_path, "evidence/" + final_filename

#     # =========================
#     # إنذار صوتي
#     # =========================
#     def play_alarm(self):
#         try:
#             winsound.Beep(2000, 700)
#         except:
#             pass

#     # =========================
#     # إرسال حالة غش
#     # =========================
#     def send_cheating_event(self, cheating, frame, cap):
#         cheating_type_id = cheating["cheating_type_id"]
#         current_time = time.time()

#         if cheating_type_id in self.last_cheating_time:
#             if current_time - self.last_cheating_time[cheating_type_id] < self.cooldown:
#                 return

#         self.last_cheating_time[cheating_type_id] = current_time

#         try:
#             snapshot_full, snapshot_relative = self.save_snapshot(frame)
#             video_full, video_relative = self.save_video_clip(cap)

#             if video_relative:
#                 print(f"🎬 الفيديو جاهز للعرض: {video_relative}")
#             else:
#                 print("⚠ لن يتم إرسال فيديو")

#             data = {
#                 "student_id": self.student_id,
#                 "cheating_type_id": cheating_type_id,
#                 "status": "suspected",
#                 "confidence_score": cheating["confidence"],
#                 "snapshot_path": snapshot_relative,
#                 "video_path": video_relative if video_relative else None
#             }

#             print("📡 جاري الإرسال للسيرفر...")
#             print(data)
#             response = requests.post(
#                 "http://127.0.0.1:8000/cheating-events/",
#                 json=data
#             )
#             print(f"📥 رد السيرفر: {response.status_code}")
#             print(f"🚨 حالة غش: {cheating['type_ar']}")

#             self.play_alarm()

#             # إرسال إيميل
#             self.email_service.send_cheating_alert(
#                 student_name=self.student_name,
#                 student_number=self.student_id,
#                 cheating_type=cheating["type_ar"],
#                 confidence=cheating["confidence"],
#                 snapshot_path=snapshot_full,
#                 video_path=video_full
#             )
#             print("📧 تم إرسال الإيميل")

#         except Exception as e:
#             print("❌ خطأ:", e)

#     # =========================
#     # تشغيل النظام
#     # =========================
#     def start_monitoring(self):
#         cap = cv2.VideoCapture(0)
#         if not cap.isOpened():
#             print("❌ لا يمكن فتح الكاميرا")
#             return

#         print("🎥 تم تشغيل الكاميرا")
#         self.audio_service.start()
#         start_time = time.time()

#         # تحديد FPS للـ buffer
#         fps = cap.get(cv2.CAP_PROP_FPS) or 20
#         self.frame_buffer = deque(maxlen=int(fps * 3))  # 3 ثواني قبل الغش

#         while True:
#             ret, frame = cap.read()
#             if not ret:
#                 break

#             self.frame_buffer.append(frame.copy())

#             # التحقق من الهوية
#             if not self.identity_verified:
#                 if time.time() - start_time <= 5:
#                     result = self.face_service.identify_student(frame)
#                     if result["match"]:
#                         self.identity_verified = True
#                         self.student_id = result["student_id"]
#                         self.student_name = result["student_name"]
#                         print(f"✅ تم التعرف على الطالب: {self.student_name}")
#                 else:
#                     print("❌ فشل التحقق من الهوية")
#                     break
#             else:
#                 cv2.putText(frame, "Exam Started", (20, 40),
#                             cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)

#                 cheating_events = []
#                 cheating_events.extend(self.object_detector.detect_cheating(frame))

#                 head = self.head_pose_service.detect_head_pose(frame)
#                 if head:
#                     cheating_events.append(head)

#                 audio = self.audio_service.detect_noise()
#                 if audio:
#                     cheating_events.append(audio)

#                 for cheating in cheating_events:
#                     self.send_cheating_event(cheating, frame, cap)
#                     cv2.putText(frame, f"Cheating: {cheating['type_ar']}",
#                                 (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

#             cv2.imshow("Exam Monitoring", frame)
#             if cv2.waitKey(1) & 0xFF == 27:  # ESC للخروج
#                 break

#         self.audio_service.stop()
#         cap.release()
#         cv2.destroyAllWindows()
# -------------------------------------------
import cv2
import time
import requests
import os
import subprocess
import winsound
from collections import deque
from app.services.face_service import FaceService
from app.services.object_detection import ObjectDetectionService
from app.services.head_pose_service import HeadPoseService
from app.services.audio_service import AudioService
from app.services.email_service import EmailService
import pymysql  # استخدم PyMySQL بدل mysql.connector

class VideoMonitoringService:
    def __init__(self):
        # =========================
        # خدمات النظام
        # =========================
        self.face_service = FaceService()
        self.object_detector = ObjectDetectionService()
        self.head_pose_service = HeadPoseService()
        self.audio_service = AudioService()
        self.email_service = EmailService()

        # =========================
        # بيانات الطالب
        # =========================
        self.identity_verified = False
        self.student_id = None
        self.student_name = None

        # =========================
        # منع التكرار
        # =========================
        self.last_cheating_time = {}
        self.cooldown = 5  # ثواني

        # =========================
        # إعدادات النظام الافتراضية
        # =========================
        self.video_before_seconds = 3
        self.video_after_seconds = 7
        self.email_enabled = True
        self.save_video = True
        self.save_snapshot = True

        # =========================
        # تحميل الإعدادات من قاعدة البيانات
        # =========================
        try:
            conn = pymysql.connect(
                host="localhost",
                user="root",
                password="",
                database="exam_monitoring",
                charset="utf8mb4",
                cursorclass=pymysql.cursors.DictCursor
            )
            cursor = conn.cursor()
            cursor.execute("SELECT setting_key, setting_value FROM settings")
            settings = cursor.fetchall()
            for s in settings:
                key = s["setting_key"]
                value = s["setting_value"]
                if key == "video_before_seconds":
                    self.video_before_seconds = int(value)
                elif key == "video_after_seconds":
                    self.video_after_seconds = int(value)
                elif key == "email_enabled":
                    self.email_enabled = value == "1"
                elif key == "save_video":
                    self.save_video = value == "1"
                elif key == "save_snapshot":
                    self.save_snapshot = value == "1"
            cursor.close()
            conn.close()
            print("✅ تم تحميل إعدادات النظام من قاعدة البيانات")
        except Exception as e:
            print("⚠ فشل تحميل الإعدادات:", e)

        # =========================
        # مجلد الأدلة
        # =========================
        self.evidence_dir = "C:/xampp/htdocs/exam_monitoring2/evidence"
        os.makedirs(self.evidence_dir, exist_ok=True)

        self.exam_started = False
        self.frame_buffer = deque()  # سيتم تحديد maxlen بعد معرفة FPS

    # =========================
    # حفظ صورة
    # =========================
    def save_snapshot(self, frame):
        if not self.save_snapshot:
            return None, None
        timestamp = int(time.time())
        filename = f"snapshot_{timestamp}.jpg"
        full_path = os.path.join(self.evidence_dir, filename)
        cv2.imwrite(full_path, frame)
        print(f"📸 تم حفظ الصورة: {full_path}")
        return full_path, "evidence/" + filename

    # =========================
    # تحويل الفيديو لـ H.264
    # =========================
    def _convert_to_h264(self, input_path, output_path):
        try:
            cmd = [
                "ffmpeg", "-y",
                "-i", input_path,
                "-c:v", "libx264",
                "-preset", "fast",
                "-crf", "23",
                "-pix_fmt", "yuv420p",
                "-movflags", "+faststart",
                "-an",
                output_path
            ]
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
            if result.returncode != 0:
                print("❌ FFmpeg error:", result.stderr.decode())
                return False
            print("✅ تم التحويل لـ H.264 بنجاح")
            return True
        except FileNotFoundError:
            print("❌ FFmpeg غير مثبت — شغّل: winget install ffmpeg")
            return False
        except subprocess.TimeoutExpired:
            print("❌ FFmpeg استغرق وقتاً طويلاً")
            return False

    # =========================
    # حفظ فيديو MP4
    # =========================
    def save_video_clip(self, cap):
        if not self.save_video or len(self.frame_buffer) == 0:
            print("⚠ لن يتم حفظ الفيديو")
            return None, None

        timestamp = int(time.time())
        temp_filename = f"temp_{timestamp}.avi"
        final_filename = f"video_{timestamp}.mp4"
        temp_path = os.path.join(self.evidence_dir, temp_filename)
        full_path = os.path.join(self.evidence_dir, final_filename)

        height, width, _ = self.frame_buffer[0].shape
        fourcc = cv2.VideoWriter_fourcc(*"MJPG")
        out = cv2.VideoWriter(temp_path, fourcc, 20.0, (width, height))

        if not out.isOpened():
            print("❌ فشل إنشاء الفيديو المؤقت")
            return None, None

        # حفظ فريمات قبل الغش
        for f in self.frame_buffer:
            out.write(f)

        # حفظ فريمات بعد الغش
        fps = cap.get(cv2.CAP_PROP_FPS) or 20
        frames_after = int(fps * self.video_after_seconds)
        for _ in range(frames_after):
            ret, frame = cap.read()
            if not ret:
                break
            out.write(frame)

        out.release()

        success = self._convert_to_h264(temp_path, full_path)
        if os.path.exists(temp_path):
            os.remove(temp_path)
        if not success:
            return None, None

        print(f"🎬 تم حفظ الفيديو: {full_path}")
        return full_path, "evidence/" + final_filename

    # =========================
    # إنذار صوتي
    # =========================
    def play_alarm(self):
        try:
            winsound.Beep(2000, 700)
        except:
            pass

    # =========================
    # إرسال حالة الغش
    # =========================
    def send_cheating_event(self, cheating, frame, cap):
        cheating_type_id = cheating["cheating_type_id"]
        current_time = time.time()
        if cheating_type_id in self.last_cheating_time:
            if current_time - self.last_cheating_time[cheating_type_id] < self.cooldown:
                return
        self.last_cheating_time[cheating_type_id] = current_time

        try:
            snapshot_full, snapshot_relative = self.save_snapshot(frame)
            video_full, video_relative = self.save_video_clip(cap)

            data = {
                "student_id": self.student_id,
                "cheating_type_id": cheating_type_id,
                "status": "suspected",
                "confidence_score": cheating["confidence"],
                "snapshot_path": snapshot_relative,
                "video_path": video_relative if video_relative else None
            }

            print("📡 جاري الإرسال للسيرفر...")
            print(data)
            response = requests.post("http://127.0.0.1:8000/cheating-events/", json=data)
            print(f"📥 رد السيرفر: {response.status_code}")
            print(f"🚨 حالة غش: {cheating['type_ar']}")

            self.play_alarm()

            if self.email_enabled:
                self.email_service.send_cheating_alert(
                    student_name=self.student_name,
                    student_number=self.student_id,
                    cheating_type=cheating["type_ar"],
                    confidence=cheating["confidence"],
                    snapshot_path=snapshot_full if self.save_snapshot else None,
                    video_path=video_full if self.save_video else None
                )
                print("📧 تم إرسال الإيميل")

        except Exception as e:
            print("❌ خطأ:", e)

    # =========================
    # تشغيل النظام
    # =========================
    def start_monitoring(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ لا يمكن فتح الكاميرا")
            return

        print("🎥 تم تشغيل الكاميرا")
        self.audio_service.start()
        start_time = time.time()

        fps = cap.get(cv2.CAP_PROP_FPS) or 20
        self.frame_buffer = deque(maxlen=int(fps * self.video_before_seconds))

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            self.frame_buffer.append(frame.copy())

            # التحقق من الهوية
            if not self.identity_verified:
                if time.time() - start_time <= 5:
                    result = self.face_service.identify_student(frame)
                    if result["match"]:
                        self.identity_verified = True
                        self.student_id = result["student_id"]
                        self.student_name = result["student_name"]
                        print(f"✅ تم التعرف على الطالب: {self.student_name}")
                else:
                    print("❌ فشل التحقق من الهوية")
                    break
            else:
                cv2.putText(frame, "Exam Started", (20, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)

                cheating_events = []
                cheating_events.extend(self.object_detector.detect_cheating(frame))

                head = self.head_pose_service.detect_head_pose(frame)
                if head:
                    cheating_events.append(head)

                audio = self.audio_service.detect_noise()
                if audio:
                    cheating_events.append(audio)

                for cheating in cheating_events:
                    self.send_cheating_event(cheating, frame, cap)
                    cv2.putText(frame, f"Cheating: {cheating['type_ar']}",
                                (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

            cv2.imshow("Exam Monitoring", frame)
            if cv2.waitKey(1) & 0xFF == 27:  # ESC للخروج
                break

        self.audio_service.stop()
        cap.release()
        cv2.destroyAllWindows()
        