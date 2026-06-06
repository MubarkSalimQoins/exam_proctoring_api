# import cv2
# from insightface.app import FaceAnalysis

# # تهيئة النموذج للعمل على CPU
# app = FaceAnalysis(name="buffalo_l")
# app.prepare(ctx_id=-1)

# print("INSIGHTFACE READY")

# # تشغيل الكاميرا
# cap = cv2.VideoCapture(0)

# while True:
#     ret, frame = cap.read()
#     if not ret:
#         print("فشل في التقاط الصورة")
#         break

#     # كشف الوجوه
#     faces = app.get(frame)

#     # رسم مستطيلات على الوجوه
#     for face in faces:
#         x1, y1, x2, y2 = face.bbox.astype(int)
#         cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
#         cv2.putText(frame, f"{face.det_score:.2f}", (x1, y1-10),
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

#     cv2.imshow("InsightFace Detection", frame)

#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# cap.release()
# cv2.destroyAllWindows()
# from insightface.app import FaceAnalysis
# import cv2

# app = FaceAnalysis(name="buffalo_l")
# app.prepare(ctx_id=0)

# img = cv2.imread("test.jpg")  # ضع صورة وجه في نفس المجلد
# faces = app.get(img)

# print("Number of faces:", len(faces))

# if len(faces) > 0:
#     embedding = faces[0].embedding
#     print("Embedding length:", len(embedding))
    # -------------------------------------------- حق الفيديو زياده
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
    # تجربت تشغيل الكيمرا
# import cv2

# url = "rtsp://admin:TVSHZW@192.168.137.225:554/Streaming/Channels/101"

# cap = cv2.VideoCapture(url)

# while True:
#     ret, frame = cap.read()
#     if not ret:
#         print("فشل في جلب الفيديو")
#         break

#     cv2.imshow("Camera", frame)

#     if cv2.waitKey(1) & 0xFF == 27:
#         break

# cap.release()
# cv2.destroyAllWindows()
# --------------------------------
# اختبار الفريمات
# import cv2
# import time

# # url = "rtsp://admin:TVSHZW@192.168.137.32:554/Streaming/Channels/101"
# cap = cv2.VideoCapture(0)

# frame_count = 0
# start = time.time()

# while frame_count < 100:
#     ret, frame = cap.read()
#     if ret:
#         frame_count += 1

# elapsed = time.time() - start
# fps = frame_count / elapsed

# print(f"FPS الفعلي: {fps:.2f}")
# cap.release()
# -------------------------------------
# اختبار الفريمات والدقه
# import cv2

# url = "rtsp://admin:TVSHZW@192.168.137.225:554/Streaming/Channels/101"
# cap = cv2.VideoCapture(url)

# if cap.isOpened():
#     width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
#     height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
#     fps = cap.get(cv2.CAP_PROP_FPS)
#     print(f"FPS: {fps}")
#     print(f"Resolution: {int(width)}x{int(height)}")

# cap.release()
# ---------------------------------- تجربه الراس بالكيمرا الخارجيه
# import cv2
# import time
# import insightface
# from collections import defaultdict
# import winsound
# import threading

# # =========================
# # 🔹 Threaded Video Capture لتجنب تعليق الفيديو
# class VideoStream:
#     def __init__(self, url):
#         self.cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
#         self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
#         self.ret, self.frame = self.cap.read()
#         self.running = True
#         self.thread = threading.Thread(target=self.update, daemon=True)
#         self.thread.start()

#     def update(self):
#         while self.running:
#             ret, frame = self.cap.read()
#             if ret:
#                 self.ret = ret
#                 self.frame = frame

#     def read(self):
#         return self.ret, self.frame

#     def stop(self):
#         self.running = False
#         self.thread.join()
#         self.cap.release()


# # =========================
# # 🔹 كشف حركة الرأس
# class HeadPoseService:

#     def __init__(self):
#         self.app = insightface.app.FaceAnalysis(name="buffalo_l")
#         self.app.prepare(ctx_id=-1)

#         # حدود الحركة
#         self.yaw_threshold = 30
#         self.pitch_threshold = 25

#         # الوقت بالثواني لتحديد الغش
#         self.required_seconds = {
#             "look_away": 0.8,
#             "head_movement": 0.8,
#             "no_face": 5
#         }

#         self.start_time = defaultdict(lambda: None)
#         self.cooldown = 5
#         self.last_reported = {}
#         print("✅ HeadPose model loaded")

#     def play_alert(self):
#         try:
#             winsound.Beep(1000, 300)
#         except:
#             pass

#     def detect_head_pose(self, frame):
#         try:
#             faces = self.app.get(frame)
#             now = time.time()

#             if len(faces) == 0:
#                 if self.start_time["no_face"] is None:
#                     self.start_time["no_face"] = now
#                 elif now - self.start_time["no_face"] >= self.required_seconds["no_face"]:
#                     last = self.last_reported.get("no_face", 0)
#                     if now - last >= self.cooldown:
#                         self.last_reported["no_face"] = now
#                         self.play_alert()
#                         return {"type_ar": "محاولة مغادرة الكاميرا"}
#                 return None
#             else:
#                 self.start_time["no_face"] = None

#             face = faces[0]
#             yaw, pitch, roll = face.pose

#             cv2.putText(frame, f"Yaw: {yaw:.1f}", (10, 30),
#                         cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
#             cv2.putText(frame, f"Pitch: {pitch:.1f}", (10, 60),
#                         cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

#             # النظر بعيد عن الشاشة
#             if abs(yaw) > self.yaw_threshold:
#                 if self.start_time["look_away"] is None:
#                     self.start_time["look_away"] = now
#                 elif now - self.start_time["look_away"] >= self.required_seconds["look_away"]:
#                     last = self.last_reported.get("look_away", 0)
#                     if now - last >= self.cooldown:
#                         self.last_reported["look_away"] = now
#                         self.play_alert()
#                         return {"type_ar": "النظر بعيداً عن الشاشة"}
#             else:
#                 self.start_time["look_away"] = None

#             # حركة رأس غير طبيعية
#             if abs(pitch) > self.pitch_threshold:
#                 if self.start_time["head_movement"] is None:
#                     self.start_time["head_movement"] = now
#                 elif now - self.start_time["head_movement"] >= self.required_seconds["head_movement"]:
#                     last = self.last_reported.get("head_movement", 0)
#                     if now - last >= self.cooldown:
#                         self.last_reported["head_movement"] = now
#                         self.play_alert()
#                         return {"type_ar": "حركة رأس غير طبيعية"}
#             else:
#                 self.start_time["head_movement"] = None

#             return None

#         except Exception as e:
#             print("Head Pose Error:", e)
#             return None


# # =========================
# # 🔹 تشغيل مستقل
# if __name__ == "__main__":
#     # رابط الكاميرا الخاصة بك
#     url = "rtsp://admin:TVSHZW@192.168.137.168:554/Streaming/Channels/101"
#     stream = VideoStream(url)
#     time.sleep(2)

#     detector = HeadPoseService()

#     print("🎥 Camera started... Press ESC to exit")

#     while True:
#         ret, frame = stream.read()
#         if not ret or frame is None:
#             continue

#         frame = cv2.resize(frame, (480, 360))  # رفع الفريمات لتسريع الأداء

#         cheating = detector.detect_head_pose(frame)

#         if cheating:
#             print(f"🚨 {cheating['type_ar']}")
#             cv2.putText(frame, cheating["type_ar"], (10, 100),
#                         cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

#         cv2.imshow("Head Pose Camera", frame)

#         if cv2.waitKey(1) & 0xFF == 27:
#             break

#     stream.stop()
#     cv2.destroyAllWindows()
    
# ------------- كود كيمرا الجهاز حق الفيديو
import cv2
import time
import requests
import os
import subprocess
import winsound
from collections import deque
import threading
from queue import Queue
from app.services.face_service import FaceService
from app.services.object_detection import ObjectDetectionService
from app.services.head_pose_service import HeadPoseService
from app.services.audio_service import AudioService
from app.services.email_service import EmailService
import pymysql  # PyMySQL للاتصال بقاعدة البيانات

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
        self.enable_video = True
        self.enable_snapshot = True

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
                    self.enable_video = value == "1"
                elif key == "save_snapshot":
                    self.enable_snapshot = value == "1"
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
        # تحسينات الأداء
        # =========================
        self.frame_queue = Queue(maxsize=2)  # طابور للفريمات
        self.latest_frame = None
        self.frame_lock = threading.Lock()
        self.buffer_lock = threading.Lock()  # حماية frame_buffer
        self.processing_active = True
        self.skip_frames = 2  # معالجة كل 3 فريمات فقط
        self.frame_counter = 0

    # =========================
    # حفظ صورة
    # =========================
    def save_snapshot(self, frame):
        if not self.enable_snapshot:
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
        if not self.enable_video:
            print("⚠ لن يتم حفظ الفيديو")
            return None, None

        # نسخ الفريمات قبل الغش بشكل آمن
        with self.buffer_lock:
            if len(self.frame_buffer) == 0:
                print("⚠ لا توجد فريمات في البافر")
                return None, None
            frames_before = list(self.frame_buffer)  # نسخة آمنة من الفريمات قبل الغش

        timestamp = int(time.time())
        temp_filename = f"temp_{timestamp}.avi"
        final_filename = f"video_{timestamp}.mp4"
        temp_path = os.path.join(self.evidence_dir, temp_filename)
        full_path = os.path.join(self.evidence_dir, final_filename)

        height, width, _ = frames_before[0].shape
        fourcc = cv2.VideoWriter_fourcc(*"MJPG")
        out = cv2.VideoWriter(temp_path, fourcc, 20.0, (width, height))

        if not out.isOpened():
            print("❌ فشل إنشاء الفيديو المؤقت")
            return None, None

        # 1️⃣ حفظ فريمات قبل الغش (من البافر)
        print(f"📹 حفظ {len(frames_before)} فريم قبل الغش...")
        for f in frames_before:
            out.write(f)

        # 2️⃣ حفظ فريمات بعد الغش (حسب الإعدادات)
        fps = cap.get(cv2.CAP_PROP_FPS) or 20
        frames_after_count = int(fps * self.video_after_seconds)
        
        print(f"📹 جاري تسجيل {self.video_after_seconds} ثانية بعد الغش...")
        frames_after = []
        start_time = time.time()
        
        # جمع الفريمات لمدة video_after_seconds
        while len(frames_after) < frames_after_count:
            with self.frame_lock:
                if self.latest_frame is not None:
                    frames_after.append(self.latest_frame.copy())
            
            time.sleep(1.0 / fps)  # انتظار حسب FPS
            
            # حماية من التعليق - إذا مر وقت أطول من المتوقع
            if time.time() - start_time > self.video_after_seconds + 2:
                print("⚠ انتهى وقت التسجيل")
                break
        
        print(f"📹 حفظ {len(frames_after)} فريم بعد الغش...")
        for f in frames_after:
            out.write(f)

        out.release()

        success = self._convert_to_h264(temp_path, full_path)
        if os.path.exists(temp_path):
            os.remove(temp_path)
        if not success:
            return None, None

        total_duration = self.video_before_seconds + self.video_after_seconds
        print(f"🎬 تم حفظ الفيديو ({total_duration} ثانية): {full_path}")
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
            # حفظ الصورة والفيديو
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
            
            # إرسال للسيرفر مع timeout
            try:
                response = requests.post(
                    "http://127.0.0.1:8000/cheating-events/", 
                    json=data,
                    timeout=5  # timeout 5 ثواني
                )
                print(f"📥 رد السيرفر: {response.status_code}")
                
                if response.status_code != 200:
                    print(f"⚠ السيرفر رد بخطأ: {response.status_code}")
                    # لكن نستمر في العمل
                    
            except requests.exceptions.Timeout:
                print("⚠ انتهى وقت الاتصال بالسيرفر - الاستمرار...")
            except requests.exceptions.ConnectionError:
                print("⚠ فشل الاتصال بالسيرفر - الاستمرار...")
            except Exception as req_error:
                print(f"⚠ خطأ في الإرسال: {req_error} - الاستمرار...")

            print(f"🚨 حالة غش: {cheating['type_ar']}")
            self.play_alarm()

            # إرسال الإيميل (في حالة فشل السيرفر)
            if self.email_enabled:
                try:
                    self.email_service.send_cheating_alert(
                        student_name=self.student_name,
                        student_number=self.student_id,
                        cheating_type=cheating["type_ar"],
                        confidence=cheating["confidence"],
                        snapshot_path=snapshot_full if self.enable_snapshot else None,
                        video_path=video_full if self.enable_video else None
                    )
                    print("📧 تم إرسال الإيميل")
                except Exception as email_error:
                    print(f"⚠ فشل إرسال الإيميل: {email_error}")

        except Exception as e:
            print(f"❌ خطأ في معالجة الغش: {e}")
            # لا نوقف النظام - نستمر في العمل

    # =========================
    # معالجة الفريمات في خيط منفصل
    # =========================
    def _process_frames(self, cap):
        """معالجة الفريمات بشكل غير متزامن"""
        last_yolo_time = 0
        yolo_interval = 0.2  # YOLO أسرع - كل 0.2 ثانية (5 مرات في الثانية) بدلاً من 0.33
        
        while self.processing_active:
            try:
                with self.frame_lock:
                    if self.latest_frame is None:
                        time.sleep(0.01)
                        continue
                    frame = self.latest_frame.copy()
                
                cheating_events = []
                current_time = time.time()
                
                # معالجة YOLO (الأثقل) - بناءً على الوقت وليس عدد الفريمات
                try:
                    if current_time - last_yolo_time >= yolo_interval:
                        cheating_events.extend(self.object_detector.detect_cheating(frame))
                        last_yolo_time = current_time
                except Exception as yolo_error:
                    print(f"⚠ خطأ في YOLO: {yolo_error}")
                
                # HeadPose أخف - كل فريم
                try:
                    head = self.head_pose_service.detect_head_pose(frame)
                    if head:
                        cheating_events.append(head)
                except Exception as head_error:
                    print(f"⚠ خطأ في HeadPose: {head_error}")
                
                # Audio من thread منفصل
                try:
                    audio = self.audio_service.detect_noise()
                    if audio:
                        cheating_events.append(audio)
                except Exception as audio_error:
                    print(f"⚠ خطأ في Audio: {audio_error}")
                
                # إرسال الأحداث
                for cheating in cheating_events:
                    try:
                        self.send_cheating_event(cheating, frame, cap)
                    except Exception as send_error:
                        print(f"⚠ خطأ في إرسال الحدث: {send_error}")
                
                time.sleep(0.02)  # تقليل استهلاك CPU
                
            except Exception as e:
                print(f"⚠ خطأ عام في المعالجة: {e}")
                time.sleep(0.1)
                # نستمر في العمل حتى لو حدث خطأ

    # =========================
    # تشغيل النظام
    # =========================
    def start_monitoring(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ لا يمكن فتح الكاميرا")
            return

        # تحسينات الكاميرا
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # تقليل buffer
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        print("🎥 تم تشغيل الكاميرا")
        self.audio_service.start()
        start_time = time.time()

        fps = cap.get(cv2.CAP_PROP_FPS) or 20
        self.frame_buffer = deque(maxlen=int(fps * self.video_before_seconds))

        # بدء thread المعالجة
        processing_thread = threading.Thread(target=self._process_frames, args=(cap,))
        processing_thread.daemon = True
        processing_thread.start()

        last_cheating_display = {}
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            self.frame_counter += 1
            
            # إضافة الفريم للبافر بشكل آمن
            with self.buffer_lock:
                self.frame_buffer.append(frame.copy())
            
            # تحديث الفريم للمعالجة
            with self.frame_lock:
                self.latest_frame = frame.copy()

            # التحقق من الهوية
            if not self.identity_verified:
                if time.time() - start_time <= 5:
                    # التحقق كل 5 فريمات فقط
                    if self.frame_counter % 5 == 0:
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

            cv2.imshow("Exam Monitoring", frame)
            if cv2.waitKey(1) & 0xFF == 27:  # ESC للخروج
                break

        self.processing_active = False
        self.audio_service.stop()
        cap.release()
        cv2.destroyAllWindows()
# --------------------------------------------كود فيدو كاميرا الخارجيه
import cv2
import time
import requests
import os
import subprocess
import winsound
from collections import deque
import threading
from queue import Queue
from app.services.face_service import FaceService
from app.services.object_detection import ObjectDetectionService
from app.services.head_pose_service import HeadPoseService
from app.services.audio_service import AudioService
from app.services.email_service import EmailService
import pymysql  # PyMySQL للاتصال بقاعدة البيانات

class VideoMonitoringService:
    def __init__(self, camera_url=None):
        # =========================
        # تخزين رابط الكاميرا
        # =========================
        self.camera_url = camera_url
        
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
        self.enable_video = True
        self.enable_snapshot = True

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
                    self.enable_video = value == "1"
                elif key == "save_snapshot":
                    self.enable_snapshot = value == "1"
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
        # تحسينات الأداء
        # =========================
        self.frame_queue = Queue(maxsize=2)  # طابور للفريمات
        self.latest_frame = None
        self.frame_lock = threading.Lock()
        self.buffer_lock = threading.Lock()  # حماية frame_buffer
        self.processing_active = True
        self.skip_frames = 2  # معالجة كل 3 فريمات فقط
        self.frame_counter = 0

    # =========================
    # حفظ صورة
    # =========================
    def save_snapshot(self, frame):
        if not self.enable_snapshot:
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
        if not self.enable_video:
            print("⚠ لن يتم حفظ الفيديو")
            return None, None

        # نسخ الفريمات قبل الغش بشكل آمن
        with self.buffer_lock:
            if len(self.frame_buffer) == 0:
                print("⚠ لا توجد فريمات في البافر")
                return None, None
            frames_before = list(self.frame_buffer)  # نسخة آمنة من الفريمات قبل الغش

        timestamp = int(time.time())
        temp_filename = f"temp_{timestamp}.avi"
        final_filename = f"video_{timestamp}.mp4"
        temp_path = os.path.join(self.evidence_dir, temp_filename)
        full_path = os.path.join(self.evidence_dir, final_filename)

        height, width, _ = frames_before[0].shape
        fourcc = cv2.VideoWriter_fourcc(*"MJPG")
        out = cv2.VideoWriter(temp_path, fourcc, 20.0, (width, height))

        if not out.isOpened():
            print("❌ فشل إنشاء الفيديو المؤقت")
            return None, None

        # 1️⃣ حفظ فريمات قبل الغش (من البافر)
        print(f"📹 حفظ {len(frames_before)} فريم قبل الغش...")
        for f in frames_before:
            out.write(f)

        # 2️⃣ حفظ فريمات بعد الغش (حسب الإعدادات)
        fps = cap.get(cv2.CAP_PROP_FPS) or 20
        frames_after_count = int(fps * self.video_after_seconds)
        
        print(f"📹 جاري تسجيل {self.video_after_seconds} ثانية بعد الغش...")
        frames_after = []
        start_time = time.time()
        
        # جمع الفريمات لمدة video_after_seconds
        while len(frames_after) < frames_after_count:
            with self.frame_lock:
                if self.latest_frame is not None:
                    frames_after.append(self.latest_frame.copy())
            
            time.sleep(1.0 / fps)  # انتظار حسب FPS
            
            # حماية من التعليق - إذا مر وقت أطول من المتوقع
            if time.time() - start_time > self.video_after_seconds + 2:
                print("⚠ انتهى وقت التسجيل")
                break
        
        print(f"📹 حفظ {len(frames_after)} فريم بعد الغش...")
        for f in frames_after:
            out.write(f)

        out.release()

        success = self._convert_to_h264(temp_path, full_path)
        if os.path.exists(temp_path):
            os.remove(temp_path)
        if not success:
            return None, None

        total_duration = self.video_before_seconds + self.video_after_seconds
        print(f"🎬 تم حفظ الفيديو ({total_duration} ثانية): {full_path}")
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
            # حفظ الصورة والفيديو
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
            
            # إرسال للسيرفر مع timeout
            try:
                response = requests.post(
                    "http://127.0.0.1:8000/cheating-events/", 
                    json=data,
                    timeout=5  # timeout 5 ثواني
                )
                print(f"📥 رد السيرفر: {response.status_code}")
                
                if response.status_code != 200:
                    print(f"⚠ السيرفر رد بخطأ: {response.status_code}")
                    # طباعة تفاصيل الخطأ من السيرفر
                    try:
                        error_detail = response.json()
                        print(f"📄 تفاصيل الخطأ: {error_detail}")
                    except:
                        print(f"📄 رد السيرفر: {response.text[:500]}")
                    # لكن نستمر في العمل
                    
            except requests.exceptions.Timeout:
                print("⚠ انتهى وقت الاتصال بالسيرفر - الاستمرار...")
            except requests.exceptions.ConnectionError:
                print("⚠ فشل الاتصال بالسيرفر - الاستمرار...")
            except Exception as req_error:
                print(f"⚠ خطأ في الإرسال: {req_error} - الاستمرار...")

            print(f"🚨 حالة غش: {cheating['type_ar']}")
            self.play_alarm()

            # إرسال الإيميل (في حالة فشل السيرفر)
            if self.email_enabled:
                try:
                    self.email_service.send_cheating_alert(
                        student_name=self.student_name,
                        student_number=self.student_id,
                        cheating_type=cheating["type_ar"],
                        confidence=cheating["confidence"],
                        snapshot_path=snapshot_full if self.enable_snapshot else None,
                        video_path=video_full if self.enable_video else None
                    )
                    print("📧 تم إرسال الإيميل")
                except Exception as email_error:
                    print(f"⚠ فشل إرسال الإيميل: {email_error}")

        except Exception as e:
            print(f"❌ خطأ في معالجة الغش: {e}")
            # لا نوقف النظام - نستمر في العمل

    # =========================
    # معالجة الفريمات في خيط منفصل
    # =========================
    def _process_frames(self, cap):
        """معالجة الفريمات بشكل غير متزامن"""
        last_yolo_time = 0
        yolo_interval = 0.15  # YOLO أسرع جداً - كل 0.15 ثانية (~7 مرات في الثانية) للكشف الفوري
        
        while self.processing_active:
            try:
                with self.frame_lock:
                    if self.latest_frame is None:
                        time.sleep(0.01)
                        continue
                    frame = self.latest_frame.copy()
                
                cheating_events = []
                current_time = time.time()
                
                # معالجة YOLO (الأثقل) - بناءً على الوقت وليس عدد الفريمات
                try:
                    if current_time - last_yolo_time >= yolo_interval:
                        cheating_events.extend(self.object_detector.detect_cheating(frame))
                        last_yolo_time = current_time
                except Exception as yolo_error:
                    print(f"⚠ خطأ في YOLO: {yolo_error}")
                
                # HeadPose أخف - كل فريم
                try:
                    head = self.head_pose_service.detect_head_pose(frame)
                    if head:
                        cheating_events.append(head)
                except Exception as head_error:
                    print(f"⚠ خطأ في HeadPose: {head_error}")
                
                # Audio من thread منفصل
                try:
                    audio = self.audio_service.detect_noise()
                    if audio:
                        cheating_events.append(audio)
                except Exception as audio_error:
                    print(f"⚠ خطأ في Audio: {audio_error}")
                
                # إرسال الأحداث
                for cheating in cheating_events:
                    try:
                        self.send_cheating_event(cheating, frame, cap)
                    except Exception as send_error:
                        print(f"⚠ خطأ في إرسال الحدث: {send_error}")
                
                time.sleep(0.02)  # تقليل استهلاك CPU
                
            except Exception as e:
                print(f"⚠ خطأ عام في المعالجة: {e}")
                time.sleep(0.1)
                # نستمر في العمل حتى لو حدث خطأ

    # =========================
    # تشغيل النظام
    # =========================
    def start_monitoring(self):
        # =========================
        # إعدادات الكاميرا
        # =========================
        # استخدام الكاميرا الخارجية (RTSP)
        url = "rtsp://admin:TVSHZW@192.168.137.138:554/Streaming/Channels/101"
        
        # استخدام الكاميرا الداخلية (USB/Webcam)
        # cap = cv2.VideoCapture(0)
        
        # استخدام الرابط الممرر أو الكاميرا الداخلية
        camera_url = self.camera_url if self.camera_url else 0
        
        if isinstance(camera_url, str):
            print(f"🔗 جاري الاتصال بالكاميرا: {camera_url}")
        else:
            print("🔗 جاري استخدام الكاميرا الداخلية...")
        cap = cv2.VideoCapture(camera_url)
        
        if not cap.isOpened():
            print("❌ فشل فتح الكاميرا الخارجية، جاري استخدام الكاميرا الداخلية...")
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                print("❌ لا يمكن فتح أي كاميرا")
                return

        print("✅ تم فتح الكاميرا بنجاح")

        # تحسينات الكاميرا
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # تقليل buffer
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        # فحص الكاميرا
        ret, test_frame = cap.read()
        if not ret:
            print("⚠️ الكاميرا مفتوحة لكن لا تقرأ فريمات!")
            # جرب fallback
            cap.release()
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                print("❌ لا يمكن قراءة من أي كاميرا")
                return
        
        print("🎥 تم تشغيل الكاميرا بنجاح")
        
        # تصغير حجم النافذة
        cv2.namedWindow("Exam Monitoring", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Exam Monitoring", 700, 500)  # حجم أصغر
        cv2.moveWindow("Exam Monitoring", 100, 50)  # موقع النافذة
        self.audio_service.start()
        start_time = time.time()

        fps = cap.get(cv2.CAP_PROP_FPS) or 20
        self.frame_buffer = deque(maxlen=int(fps * self.video_before_seconds))

        # بدء thread المعالجة
        processing_thread = threading.Thread(target=self._process_frames, args=(cap,))
        processing_thread.daemon = True
        processing_thread.start()

        last_cheating_display = {}
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            self.frame_counter += 1
            
            # إضافة الفريم للبافر بشكل آمن
            with self.buffer_lock:
                self.frame_buffer.append(frame.copy())
            
            # تحديث الفريم للمعالجة
            with self.frame_lock:
                self.latest_frame = frame.copy()

            # التحقق من الهوية
            if not self.identity_verified:
                if time.time() - start_time <= 5:
                    # التحقق كل 5 فريمات فقط
                    if self.frame_counter % 5 == 0:
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

            cv2.imshow("Exam Monitoring", frame)
            if cv2.waitKey(1) & 0xFF == 27:  # ESC للخروج
                break

        self.processing_active = False
        self.audio_service.stop()
        cap.release()
        cv2.destroyAllWindows()



# -------------------------------------كود كشف الهاتف 
import cv2
import time
from collections import defaultdict
from ultralytics import YOLOWorld


class ObjectDetectionService:
    def __init__(self):
        print("⏳ Loading YOLO-World model...")
        self.model = YOLOWorld("yolov8s-worldv2.pt")
        
        # تحسينات الأداء
        self.model.overrides['conf'] = 0.25  # threshold أعلى
        self.model.overrides['iou'] = 0.45
        self.model.overrides['half'] = False  # FP16 للسرعة (إذا كان GPU متاح)

        self.earphone_aliases = [
            "earphone", "earphones", "earbuds", "earbud",
            "headphones", "headphone", "wireless earbuds",
            "in-ear headphones", "airpods",
        ]

        all_classes = self.earphone_aliases + [
            "cell phone", "person", "mobile phone", "smartphone"
        ]
        self.model.set_classes(all_classes)

        self.cheating_map = {alias: "استخدام سماعات" for alias in self.earphone_aliases}
        self.cheating_map["cell phone"] = "استخدام الهاتف"
        self.cheating_map["mobile phone"] = "استخدام الهاتف"
        self.cheating_map["smartphone"] = "استخدام الهاتف"

        self.cheating_type_ids = {
            "استخدام الهاتف": 1,#4
            "استخدام سماعات": 3,#3
            "وجود شخص آخر": 2,#2
        }
        

        self.phone_threshold = 0.30  # تقليل من 0.40 لكشف أسرع
        self.earphone_threshold = 0.35

        # كشف فوري - فريم واحد فقط
        self.confirm_frames_needed = {
            "استخدام الهاتف": 1,  # فوري
            "استخدام سماعات": 2,
            "وجود شخص آخر": 1,  # فوري للشخص الثاني
        }

        self.consecutive_count = defaultdict(int)

        self.cooldown = 5  # cooldown عام
        self.phone_cooldown = 2  # cooldown للهاتف - سريع
        self.person_cooldown = 2  # cooldown للشخص الثاني - سريع
        self.last_reported = {}

        print("✅ Model loaded successfully")

    # =========================
    # الكشف الأساسي
    # =========================
    def detect(self, frame):
        # تصغير الفريم لتسريع المعالجة
        height, width = frame.shape[:2]
        if width > 640:
            scale = 640 / width
            new_width = 640
            new_height = int(height * scale)
            frame_resized = cv2.resize(frame, (new_width, new_height))
        else:
            frame_resized = frame
            
        results = self.model(frame_resized, verbose=False, imgsz=640)

        found_types = set()
        person_detections = []

        for result in results:
            for box in result.boxes:
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                label = self.model.names[class_id].lower()

                # جمع معلومات الأشخاص
                if label == "person":
                    # فقط الأشخاص بثقة عالية
                    if confidence > 0.5:
                        x1, y1, x2, y2 = box.xyxy[0].tolist()
                        area = (x2 - x1) * (y2 - y1)
                        person_detections.append({
                            'confidence': confidence,
                            'area': area,
                            'box': (x1, y1, x2, y2)
                        })
                    continue

                # كشف الغش
                if label in self.cheating_map:
                    cheating_type = self.cheating_map[label]

                    threshold = (
                        self.phone_threshold
                        if "هاتف" in cheating_type
                        else self.earphone_threshold
                    )

                    if confidence < threshold:
                        continue

                    found_types.add((cheating_type, label, confidence))

        # فلترة الأشخاص - إزالة الكشوفات الصغيرة والضعيفة
        if len(person_detections) > 1:
            # ترتيب حسب المساحة (الأكبر أولاً)
            person_detections.sort(key=lambda x: x['area'], reverse=True)
            
            # الشخص الرئيسي (الأكبر)
            main_person = person_detections[0]
            
            # فحص الأشخاص الآخرين
            real_persons = 1
            for person in person_detections[1:]:
                # إذا كان الشخص الآخر كبير بما يكفي (أكثر من 30% من الرئيسي)
                # وثقة عالية (أكثر من 0.65)
                if person['area'] > main_person['area'] * 0.3 and person['confidence'] > 0.65:
                    real_persons += 1
            
            # فقط إذا كان هناك شخصان حقيقيان
            if real_persons > 1:
                found_types.add(("وجود شخص آخر", "multiple_persons", 1.0))

        # =========================
        # نظام التأكيد + cooldown
        # =========================
        confirmed_detections = []
        all_cheating_types = set(ct for ct, _, _ in found_types)

        for cheating_type, label, confidence in found_types:
            self.consecutive_count[cheating_type] += 1
            needed = self.confirm_frames_needed.get(cheating_type, 3)

            if self.consecutive_count[cheating_type] >= needed:
                now = time.time()
                last = self.last_reported.get(cheating_type, 0)
                
                # استخدام cooldown مختلف حسب النوع
                if "هاتف" in cheating_type:
                    cooldown_time = self.phone_cooldown
                elif "شخص" in cheating_type:
                    cooldown_time = self.person_cooldown
                else:
                    cooldown_time = self.cooldown

                if now - last >= cooldown_time:
                    self.last_reported[cheating_type] = now

                    confirmed_detections.append({
                        "label": label,
                        "confidence": confidence,
                        "type_ar": cheating_type,
                        "cheating_type_id": self.cheating_type_ids.get(cheating_type, 0),
                    })

        # إعادة التصفير
        for cheating_type in list(self.consecutive_count.keys()):
            if cheating_type not in all_cheating_types:
                self.consecutive_count[cheating_type] = 0

        return confirmed_detections

    # =========================
    # هذه هي المهمة (مطلوبة من video_service)
    # =========================
    def detect_cheating(self, frame):
        return self.detect(frame)


# =========================
# تشغيل للاختبار فقط
# =========================
if __name__ == "__main__":
    detector = ObjectDetectionService()
    cap = cv2.VideoCapture(0)

    print("🎥 Camera started...")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        detections = detector.detect_cheating(frame)

        for d in detections:
            print(f"🚨 {d['type_ar']} | {d['label']} | {d['confidence']:.2f}")

        cv2.imshow("Test", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


