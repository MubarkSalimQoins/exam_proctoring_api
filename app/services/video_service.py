# # # --------------------------------
# import cv2
# import time
# import requests
# import os
# import subprocess
# import winsound
# from collections import deque
# import threading
# import pymysql

# from app.services.face_service import FaceService
# from app.services.object_detection import ObjectDetectionService
# from app.services.head_pose_service import HeadPoseService
# from app.services.audio_service import AudioService
# from app.services.email_service import EmailService


# # =========================
# # Threaded Camera
# # =========================
# class VideoStream:
#     def __init__(self, source):
#         self.cap = cv2.VideoCapture(source, cv2.CAP_FFMPEG)
#         self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

#         self.ret, self.frame = self.cap.read()
#         self.running = True
#         self.lock = threading.Lock()

#         threading.Thread(target=self.update, daemon=True).start()

#     def update(self):
#         while self.running:
#             ret, frame = self.cap.read()
#             if ret:
#                 with self.lock:
#                     self.ret = ret
#                     self.frame = frame

#     def read(self):
#         with self.lock:
#             return self.ret, self.frame.copy() if self.frame is not None else None

#     def stop(self):
#         self.running = False
#         self.cap.release()


# # =========================
# # النظام الرئيسي
# # =========================
# class VideoMonitoringService:
#     def __init__(self, camera_source):
#         self.face_service = FaceService()
#         self.object_detector = ObjectDetectionService()
#         self.head_pose_service = HeadPoseService()
#         self.audio_service = AudioService()
#         self.email_service = EmailService()

#         self.identity_verified = False
#         self.student_id = None
#         self.student_name = None

#         self.last_cheating_time = {}
#         self.cooldown = 5

#         self.video_before_seconds = 3
#         self.video_after_seconds = 7
#         self.enable_video = True
#         self.enable_snapshot = True

#         try:
#             conn = pymysql.connect(
#                 host="localhost",
#                 user="root",
#                 password="",
#                 database="exam_monitoring",
#                 charset="utf8mb4",
#                 cursorclass=pymysql.cursors.DictCursor
#             )
#             cursor = conn.cursor()
#             cursor.execute("SELECT setting_key, setting_value FROM settings")
#             for s in cursor.fetchall():
#                 if s["setting_key"] == "video_before_seconds":
#                     self.video_before_seconds = int(s["setting_value"])
#                 elif s["setting_key"] == "video_after_seconds":
#                     self.video_after_seconds = int(s["setting_value"])
#                 elif s["setting_key"] == "save_video":
#                     self.enable_video = s["setting_value"] == "1"
#                 elif s["setting_key"] == "save_snapshot":
#                     self.enable_snapshot = s["setting_value"] == "1"
#             conn.close()
#         except:
#             pass

#         self.evidence_dir = "C:/xampp/htdocs/exam_monitoring2/evidence"
#         os.makedirs(self.evidence_dir, exist_ok=True)

#         self.camera_source = camera_source
#         self.stream = None
#         self.frame_buffer = deque()
#         self.fps = 20

#     def save_snapshot(self, frame):
#         if not self.enable_snapshot:
#             return None, None

#         filename = f"snapshot_{int(time.time())}.jpg"
#         path = os.path.join(self.evidence_dir, filename)
#         cv2.imwrite(path, frame)

#         return path, "evidence/" + filename

#     def _convert_to_h264(self, input_path, output_path):
#         cmd = [
#             "ffmpeg", "-y",
#             "-i", input_path,
#             "-c:v", "libx264",
#             "-preset", "fast",
#             "-crf", "23",
#             "-pix_fmt", "yuv420p",
#             output_path
#         ]
#         subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

#     def save_video_clip(self):
#         if not self.enable_video or len(self.frame_buffer) == 0:
#             return None, None

#         timestamp = int(time.time())
#         temp_path = os.path.join(self.evidence_dir, f"temp_{timestamp}.avi")
#         final_path = os.path.join(self.evidence_dir, f"video_{timestamp}.mp4")

#         h, w, _ = self.frame_buffer[0].shape
#         out = cv2.VideoWriter(temp_path, cv2.VideoWriter_fourcc(*"MJPG"), self.fps, (w, h))

#         for f in self.frame_buffer:
#             out.write(f)

#         frames_after = int(self.fps * self.video_after_seconds)
#         for _ in range(frames_after):
#             ret, frame = self.stream.read()
#             if not ret:
#                 break
#             out.write(frame)

#         out.release()
#         self._convert_to_h264(temp_path, final_path)

#         os.remove(temp_path)

#         return final_path, "evidence/" + os.path.basename(final_path)

#     # =========================
#     # ✅ تم تعديلها لإضافة الإيميل
#     # =========================
#     def send_cheating_event(self, cheating, frame):
#         now = time.time()

#         if cheating["cheating_type_id"] in self.last_cheating_time:
#             if now - self.last_cheating_time["cheating_type_id"] < self.cooldown:
#                 return

#         self.last_cheating_time["cheating_type_id"] = now

#         snapshot_full, snapshot_rel = self.save_snapshot(frame)
#         video_full, video_rel = self.save_video_clip()

#         data = {
#             "student_id": self.student_id,
#             "cheating_type_id": cheating["cheating_type_id"],
#             "status": "suspected",
#             "confidence_score": cheating.get("confidence", 1.0),
#             "snapshot_path": snapshot_rel,
#             "video_path": video_rel
#         }

#         try:
#             response = requests.post("http://127.0.0.1:8000/cheating-events/", json=data)
#             print("✅ تم الإرسال للـ API:", response.status_code)
#         except Exception as e:
#             print("❌ فشل الإرسال للـ API:", e)

#         # =========================
#         # 📧 إرسال الإيميل
#         # =========================
#         try:
#             print("📧 جاري إرسال الإيميل...")
#             self.email_service.send_cheating_alert(
#                 student_name=self.student_name,
#                 student_number=self.student_id,
#                 cheating_type=cheating["type_ar"],
#                 # cheating_type=cheating["cheating_type_id"], يرسل رقم الغش
#                 confidence=round(cheating.get("confidence", 1.0) * 100, 2),
#                 snapshot_path=snapshot_full,
#                 video_path=video_full
#             )
#             print("📧 تم إرسال الإيميل بنجاح")
#         except Exception as e:
#             print("❌ خطأ في الإيميل:", e)

#         winsound.Beep(2000, 500)

#     def start_monitoring(self):
#         self.stream = VideoStream(self.camera_source)
#         time.sleep(2)

#         ret, frame = self.stream.read()
#         if not ret:
#             print("❌ الكاميرا لا تعمل")
#             return

#         self.fps = 20
#         self.frame_buffer = deque(maxlen=int(self.fps * self.video_before_seconds))

#         self.audio_service.start()
#         start_time = time.time()

#         cv2.namedWindow("Exam Monitoring", cv2.WINDOW_NORMAL)
#         cv2.resizeWindow("Exam Monitoring", 640, 480)
#         cv2.moveWindow("Exam Monitoring", 500, 200)

#         while True:
#             ret, frame = self.stream.read()
#             if not ret:
#                 continue

#             self.frame_buffer.append(frame.copy())

#             if not self.identity_verified:
#                 if time.time() - start_time <= 5:
#                     res = self.face_service.identify_student(frame)
#                     if res["match"]:
#                         self.identity_verified = True
#                         self.student_id = res["student_id"]
#                         self.student_name = res["student_name"]
#                         print("✅ تم التعرف على الطالب")
#                 else:
#                     break
#             else:
#                 events = []
#                 events.extend(self.object_detector.detect_cheating(frame))

#                 head = self.head_pose_service.detect_head_pose(frame)
#                 if head:
#                     events.append(head)

#                 audio = self.audio_service.detect_noise()
#                 if audio:
#                     events.append(audio)

#                 for e in events:
#                     self.send_cheating_event(e, frame)

#             cv2.imshow("Exam Monitoring", frame)
#             if cv2.waitKey(1) == 27:
#                 break

#         self.audio_service.stop()
#         self.stream.stop()
#         cv2.destroyAllWindows()


# # =========================
# # تشغيل
# # =========================
# if __name__ == "__main__":
#     camera_url = "rtsp://admin:TVSHZW@192.168.137.40:554/Streaming/Channels/101"
#     # camera_url = "rtsp://admin:TVSHZW@192.168.137.40:554/Streaming/Channels/102"
#     app = VideoMonitoringService(camera_url)
#     app.start_monitoring()
# ////////////////  11/5كود الكيمرا الصح حاليا 
# import cv2
# import time
# import requests
# import os
# import subprocess
# import winsound
# from collections import deque
# import threading
# import pymysql

# from app.services.face_service import FaceService
# from app.services.object_detection import ObjectDetectionService
# from app.services.head_pose_service import HeadPoseService
# from app.services.audio_service import AudioService
# from app.services.email_service import EmailService


# # =========================
# # Threaded Camera
# # =========================
# class VideoStream:
#     def __init__(self, source):
#         self.cap = cv2.VideoCapture(source, cv2.CAP_FFMPEG)
#         self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

#         self.ret, self.frame = self.cap.read()
#         self.running = True
#         self.lock = threading.Lock()

#         threading.Thread(target=self.update, daemon=True).start()

#     def update(self):
#         while self.running:
#             ret, frame = self.cap.read()
#             if ret:
#                 with self.lock:
#                     self.ret = ret
#                     self.frame = frame

#     def read(self):
#         with self.lock:
#             return self.ret, self.frame.copy() if self.frame is not None else None

#     def stop(self):
#         self.running = False
#         self.cap.release()


# # =========================
# # النظام الرئيسي
# # =========================
# class VideoMonitoringService:
#     def __init__(self, camera_source):
#         self.face_service = FaceService()
#         self.object_detector = ObjectDetectionService()
#         self.head_pose_service = HeadPoseService()
#         self.audio_service = AudioService()
#         self.email_service = EmailService()

#         self.identity_verified = False
#         self.student_id = None
#         self.student_name = None

#         self.last_cheating_time = {}
#         self.cooldown = 5

#         self.video_before_seconds = 3
#         self.video_after_seconds = 7
#         self.enable_video = True
#         self.enable_snapshot = True

#         try:
#             conn = pymysql.connect(
#                 host="localhost",
#                 user="root",
#                 password="",
#                 database="exam_monitoring",
#                 charset="utf8mb4",
#                 cursorclass=pymysql.cursors.DictCursor
#             )
#             cursor = conn.cursor()
#             cursor.execute("SELECT setting_key, setting_value FROM settings")
#             for s in cursor.fetchall():
#                 if s["setting_key"] == "video_before_seconds":
#                     self.video_before_seconds = int(s["setting_value"])
#                 elif s["setting_key"] == "video_after_seconds":
#                     self.video_after_seconds = int(s["setting_value"])
#                 elif s["setting_key"] == "save_video":
#                     self.enable_video = s["setting_value"] == "1"
#                 elif s["setting_key"] == "save_snapshot":
#                     self.enable_snapshot = s["setting_value"] == "1"
#             conn.close()
#         except:
#             pass

#         self.evidence_dir = "C:/xampp/htdocs/exam_monitoring2/evidence"
#         os.makedirs(self.evidence_dir, exist_ok=True)

#         self.camera_source = camera_source
#         self.stream = None
#         self.frame_buffer = deque()
#         self.fps = 20

#     def save_snapshot(self, frame):
#         if not self.enable_snapshot:
#             return None, None

#         filename = f"snapshot_{int(time.time())}.jpg"
#         path = os.path.join(self.evidence_dir, filename)
#         cv2.imwrite(path, frame)

#         return path, "evidence/" + filename

#     def _convert_to_h264(self, input_path, output_path):
#         cmd = [
#             "ffmpeg", "-y",
#             "-i", input_path,
#             "-c:v", "libx264",
#             "-preset", "fast",
#             "-crf", "23",
#             "-pix_fmt", "yuv420p",
#             output_path
#         ]
#         subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

#     def save_video_clip(self):
#         if not self.enable_video or len(self.frame_buffer) == 0:
#             return None, None

#         timestamp = int(time.time())
#         temp_path = os.path.join(self.evidence_dir, f"temp_{timestamp}.avi")
#         final_path = os.path.join(self.evidence_dir, f"video_{timestamp}.mp4")

#         h, w, _ = self.frame_buffer[0].shape
#         out = cv2.VideoWriter(temp_path, cv2.VideoWriter_fourcc(*"MJPG"), self.fps, (w, h))

#         for f in self.frame_buffer:
#             out.write(f)

#         frames_after = int(self.fps * self.video_after_seconds)
#         for _ in range(frames_after):
#             ret, frame = self.stream.read()
#             if not ret:
#                 break
#             out.write(frame)

#         out.release()
#         self._convert_to_h264(temp_path, final_path)

#         os.remove(temp_path)

#         return final_path, "evidence/" + os.path.basename(final_path)

#     # =========================
#     # ✅ تم تعديلها لإضافة الإيميل
#     # =========================
#     def send_cheating_event(self, cheating, frame):
#         now = time.time()

#         if cheating["cheating_type_id"] in self.last_cheating_time:
#             if now - self.last_cheating_time["cheating_type_id"] < self.cooldown:
#                 return

#         self.last_cheating_time["cheating_type_id"] = now

#         snapshot_full, snapshot_rel = self.save_snapshot(frame)
#         video_full, video_rel = self.save_video_clip()

#         data = {
#             "student_id": self.student_id,
#             "cheating_type_id": cheating["cheating_type_id"],
#             "status": "suspected",
#             "confidence_score": cheating.get("confidence", 1.0),
#             "snapshot_path": snapshot_rel,
#             "video_path": video_rel
#         }

#         try:
#             response = requests.post("http://127.0.0.1:8000/cheating-events/", json=data)
#             print("✅ تم الإرسال للـ API:", response.status_code)
#         except Exception as e:
#             print("❌ فشل الإرسال للـ API:", e)

#         # =========================
#         # 📧 إرسال الإيميل
#         # =========================
#         try:
#             print("📧 جاري إرسال الإيميل...")
#             self.email_service.send_cheating_alert(
#                 student_name=self.student_name,
#                 student_number=self.student_id,
#                 cheating_type=cheating["type_ar"],
#                 # cheating_type=cheating["cheating_type_id"], يرسل رقم الغش
#                 confidence=round(cheating.get("confidence", 1.0) * 100, 2),
#                 snapshot_path=snapshot_full,
#                 video_path=video_full
#             )
#             print("📧 تم إرسال الإيميل بنجاح")
#         except Exception as e:
#             print("❌ خطأ في الإيميل:", e)

#         winsound.Beep(2000, 500)

#     def start_monitoring(self):
#         self.stream = VideoStream(self.camera_source)
#         time.sleep(2)

#         ret, frame = self.stream.read()
#         if not ret:
#             print("❌ الكاميرا لا تعمل")
#             return

#         self.fps = 20
#         self.frame_buffer = deque(maxlen=int(self.fps * self.video_before_seconds))

#         self.audio_service.start()
#         start_time = time.time()

#         cv2.namedWindow("Exam Monitoring", cv2.WINDOW_NORMAL)
#         cv2.resizeWindow("Exam Monitoring", 640, 480)
#         cv2.moveWindow("Exam Monitoring", 500, 200)

#         while True:
#             ret, frame = self.stream.read()
#             if not ret:
#                 continue

#             self.frame_buffer.append(frame.copy())

#             if not self.identity_verified:
#                 if time.time() - start_time <= 5:
#                     res = self.face_service.identify_student(frame)
#                     if res["match"]:
#                         self.identity_verified = True
#                         self.student_id = res["student_id"]
#                         self.student_name = res["student_name"]
#                         print("✅ تم التعرف على الطالب")
#                 else:
#                     break
#             else:
#                 events = []
#                 events.extend(self.object_detector.detect_cheating(frame))
#                 # events.extend(self.head_pose_service.detect_cheating(frame))
#                 cheating = self.head_pose_service.detect_head_pose(frame)

#                 if cheating:
#                    events.append(cheating)

#                 audio = self.audio_service.detect_noise()
#                 if audio:
#                     events.append(audio)

#                 for e in events:
#                     self.send_cheating_event(e, frame)

#             cv2.imshow("Exam Monitoring", frame)
#             if cv2.waitKey(1) == 27:
#                 break

#         self.audio_service.stop()
#         self.stream.stop()
#         cv2.destroyAllWindows()


# # =========================
# # تشغيل
# # =========================
# if __name__ == "__main__":
#     camera_url = "rtsp://admin:TVSHZW@192.168.137.40:554/Streaming/Channels/101"
#     app = VideoMonitoringService(camera_url)
#     app.start_monitoring()
# ////////////////////
# --------------------------
# 1كاميرا خارجيه
# import cv2
# import time
# import requests
# import os
# import subprocess
# import winsound
# from collections import deque
# import threading
# import pymysql

# from app.services.face_service import FaceService
# from app.services.object_detection import ObjectDetectionService
# from app.services.head_pose_service import HeadPoseService
# from app.services.audio_service import AudioService
# from app.services.email_service import EmailService


# # =========================
# # Threaded Camera
# # =========================
# class VideoStream:
#     def __init__(self, source):
#         self.cap = cv2.VideoCapture(source, cv2.CAP_FFMPEG)
#         self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

#         self.ret, self.frame = self.cap.read()
#         self.running = True
#         self.lock = threading.Lock()

#         threading.Thread(target=self.update, daemon=True).start()

#     def update(self):
#         while self.running:
#             ret, frame = self.cap.read()
#             if ret:
#                 with self.lock:
#                     self.ret = ret
#                     self.frame = frame

#     def read(self):
#         with self.lock:
#             return self.ret, self.frame.copy() if self.frame is not None else None

#     def stop(self):
#         self.running = False
#         self.cap.release()


# # =========================
# # النظام الرئيسي
# # =========================
# class VideoMonitoringService:
#     def __init__(self, camera_source):
#         self.face_service = FaceService()
#         self.object_detector = ObjectDetectionService()
#         self.head_pose_service = HeadPoseService()
#         self.audio_service = AudioService()
#         self.email_service = EmailService()

#         self.identity_verified = False
#         self.student_id = None
#         self.student_name = None

#         self.last_cheating_time = {}
#         self.cooldown = 5

#         self.video_before_seconds = 3
#         self.video_after_seconds = 7
#         self.enable_video = True
#         self.enable_snapshot = True

#         # تحميل إعدادات DB
#         try:
#             conn = pymysql.connect(
#                 host="localhost",
#                 user="root",
#                 password="",
#                 database="exam_monitoring",
#                 charset="utf8mb4",
#                 cursorclass=pymysql.cursors.DictCursor
#             )
#             cursor = conn.cursor()
#             cursor.execute("SELECT setting_key, setting_value FROM settings")
#             for s in cursor.fetchall():
#                 if s["setting_key"] == "video_before_seconds":
#                     self.video_before_seconds = int(s["setting_value"])
#                 elif s["setting_key"] == "video_after_seconds":
#                     self.video_after_seconds = int(s["setting_value"])
#                 elif s["setting_key"] == "save_video":
#                     self.enable_video = s["setting_value"] == "1"
#                 elif s["setting_key"] == "save_snapshot":
#                     self.enable_snapshot = s["setting_value"] == "1"
#             conn.close()
#         except:
#             pass

#         self.evidence_dir = "C:/xampp/htdocs/exam_monitoring2/evidence"
#         os.makedirs(self.evidence_dir, exist_ok=True)

#         self.camera_source = camera_source
#         self.stream = None
#         self.frame_buffer = deque()
#         self.fps = 20

#     # =========================
#     def save_snapshot(self, frame):
#         if not self.enable_snapshot:
#             return None, None

#         filename = f"snapshot_{int(time.time())}.jpg"
#         path = os.path.join(self.evidence_dir, filename)
#         cv2.imwrite(path, frame)

#         return path, "evidence/" + filename

#     # =========================
#     def _convert_to_h264(self, input_path, output_path):
#         cmd = [
#             "ffmpeg", "-y",
#             "-i", input_path,
#             "-c:v", "libx264",
#             "-preset", "fast",
#             "-crf", "23",
#             "-pix_fmt", "yuv420p",
#             output_path
#         ]
#         subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

#     # =========================
#     def save_video_clip(self):
#         if not self.enable_video or len(self.frame_buffer) == 0:
#             return None, None

#         timestamp = int(time.time())
#         temp_path = os.path.join(self.evidence_dir, f"temp_{timestamp}.avi")
#         final_path = os.path.join(self.evidence_dir, f"video_{timestamp}.mp4")

#         h, w, _ = self.frame_buffer[0].shape
#         out = cv2.VideoWriter(temp_path, cv2.VideoWriter_fourcc(*"MJPG"), self.fps, (w, h))

#         # قبل الغش
#         for f in self.frame_buffer:
#             out.write(f)

#         # بعد الغش
#         frames_after = int(self.fps * self.video_after_seconds)
#         for _ in range(frames_after):
#             ret, frame = self.stream.read()
#             if not ret:
#                 break
#             out.write(frame)

#         out.release()
#         self._convert_to_h264(temp_path, final_path)

#         os.remove(temp_path)

#         return final_path, "evidence/" + os.path.basename(final_path)

#     # =========================
#     def send_cheating_event(self, cheating, frame):
#         now = time.time()

#         if cheating["cheating_type_id"] in self.last_cheating_time:
#             if now - self.last_cheating_time[cheating["cheating_type_id"]] < self.cooldown:
#                 return

#         self.last_cheating_time[cheating["cheating_type_id"]] = now

#         snapshot_full, snapshot_rel = self.save_snapshot(frame)
#         video_full, video_rel = self.save_video_clip()

#         data = {
#             "student_id": self.student_id,
#             "cheating_type_id": cheating["cheating_type_id"],
#             "status": "suspected",
#             "confidence_score": cheating.get("confidence", 1.0),
#             "snapshot_path": snapshot_rel,
#             "video_path": video_rel
#         }

#         try:
#             response = requests.post("http://127.0.0.1:8000/cheating-events/", json=data)
#             print("✅ تم الإرسال:", response.status_code)
#         except Exception as e:
#             print("❌ فشل الإرسال:", e)

#         winsound.Beep(2000, 500)

#     # =========================
#     def start_monitoring(self):
#         self.stream = VideoStream(self.camera_source)
#         time.sleep(2)

#         ret, frame = self.stream.read()
#         if not ret:
#             print("❌ الكاميرا لا تعمل")
#             return

#         self.fps = 20
#         self.frame_buffer = deque(maxlen=int(self.fps * self.video_before_seconds))

#         self.audio_service.start()
#         start_time = time.time()

#         cv2.namedWindow("Exam Monitoring", cv2.WINDOW_NORMAL)
#         cv2.resizeWindow("Exam Monitoring", 640, 480)
#         cv2.moveWindow("Exam Monitoring", 500, 200)

#         while True:
#             ret, frame = self.stream.read()
#             if not ret:
#                 continue

#             self.frame_buffer.append(frame.copy())

#             if not self.identity_verified:
#                 if time.time() - start_time <= 5:
#                     res = self.face_service.identify_student(frame)
#                     if res["match"]:
#                         self.identity_verified = True
#                         self.student_id = res["student_id"]
#                         self.student_name = res["student_name"]
#                         print("✅ تم التعرف")
#                 else:
#                     break
#             else:
#                 events = []
#                 events.extend(self.object_detector.detect_cheating(frame))

#                 head = self.head_pose_service.detect_head_pose(frame)
#                 if head:
#                     events.append(head)

#                 audio = self.audio_service.detect_noise()
#                 if audio:
#                     events.append(audio)

#                 for e in events:
#                     self.send_cheating_event(e, frame)

#             cv2.imshow("Exam Monitoring", frame)
#             if cv2.waitKey(1) == 27:
#                 break

#         self.audio_service.stop()
#         self.stream.stop()
#         cv2.destroyAllWindows()


# # =========================
# # تشغيل
# # =========================
# if __name__ == "__main__":
#     camera_url = "rtsp://admin:TVSHZW@192.168.137.150:554/Streaming/Channels/101"
#     app = VideoMonitoringService(camera_url)
#     app.start_monitoring()
# -------------------------------------------
# --------------------------------------------------------------
# الصح 8/4 كاميرا الجهاز
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
# import pymysql  # PyMySQL للاتصال بقاعدة البيانات

# class VideoMonitoringService:
#     def __init__(self):
#         # =========================
#         # خدمات النظام
#         # =========================
#         self.face_service = FaceService()
#         self.object_detector = ObjectDetectionService()
#         self.head_pose_service = HeadPoseService()
#         self.audio_service = AudioService()
#         self.email_service = EmailService()

#         # =========================
#         # تعديل كشف السماعات: اكتشاف مباشر
#         # =========================
#         self.object_detector.confirm_frames_needed["استخدام سماعات"] = 1  # فريم واحد يكفي
#         self.object_detector.earphone_threshold = 0.25  # حساس أكثر للسماعات الصغيرة

#         # =========================
#         # بيانات الطالب
#         # =========================
#         self.identity_verified = False
#         self.student_id = None
#         self.student_name = None

#         # =========================
#         # منع التكرار
#         # =========================
#         self.last_cheating_time = {}
#         self.cooldown = 5  # ثواني

#         # =========================
#         # إعدادات النظام الافتراضية
#         # =========================
#         self.video_before_seconds = 3
#         self.video_after_seconds = 7
#         self.email_enabled = True
#         self.enable_video = True
#         self.enable_snapshot = True

#         # =========================
#         # تحميل الإعدادات من قاعدة البيانات
#         # =========================
#         try:
#             conn = pymysql.connect(
#                 host="localhost",
#                 user="root",
#                 password="",
#                 database="exam_monitoring",
#                 charset="utf8mb4",
#                 cursorclass=pymysql.cursors.DictCursor
#             )
#             cursor = conn.cursor()
#             cursor.execute("SELECT setting_key, setting_value FROM settings")
#             settings = cursor.fetchall()
#             for s in settings:
#                 key = s["setting_key"]
#                 value = s["setting_value"]
#                 if key == "video_before_seconds":
#                     self.video_before_seconds = int(value)
#                 elif key == "video_after_seconds":
#                     self.video_after_seconds = int(value)
#                 elif key == "email_enabled":
#                     self.email_enabled = value == "1"
#                 elif key == "save_video":
#                     self.enable_video = value == "1"
#                 elif key == "save_snapshot":
#                     self.enable_snapshot = value == "1"
#             cursor.close()
#             conn.close()
#             print("✅ تم تحميل إعدادات النظام من قاعدة البيانات")
#         except Exception as e:
#             print("⚠ فشل تحميل الإعدادات:", e)

#         # =========================
#         # مجلد الأدلة
#         # =========================
#         self.evidence_dir = "C:/xampp/htdocs/exam_monitoring2/evidence"
#         os.makedirs(self.evidence_dir, exist_ok=True)

#         self.exam_started = False
#         self.frame_buffer = deque()  # سيتم تحديد maxlen بعد معرفة FPS

#     # =========================
#     # حفظ صورة
#     # =========================
#     def save_snapshot(self, frame):
#         if not self.enable_snapshot:
#             return None, None
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
#                 "ffmpeg", "-y",
#                 "-i", input_path,
#                 "-c:v", "libx264",
#                 "-preset", "fast",
#                 "-crf", "23",
#                 "-pix_fmt", "yuv420p",
#                 "-movflags", "+faststart",
#                 "-an",
#                 output_path
#             ]
#             result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
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
#         if not self.enable_video or len(self.frame_buffer) == 0:
#             print("⚠ لن يتم حفظ الفيديو")
#             return None, None

#         timestamp = int(time.time())
#         temp_filename = f"temp_{timestamp}.avi"
#         final_filename = f"video_{timestamp}.mp4"
#         temp_path = os.path.join(self.evidence_dir, temp_filename)
#         full_path = os.path.join(self.evidence_dir, final_filename)

#         height, width, _ = self.frame_buffer[0].shape
#         fourcc = cv2.VideoWriter_fourcc(*"MJPG")
#         out = cv2.VideoWriter(temp_path, fourcc, 20.0, (width, height))

#         if not out.isOpened():
#             print("❌ فشل إنشاء الفيديو المؤقت")
#             return None, None

#         # حفظ فريمات قبل الغش
#         for f in self.frame_buffer:
#             out.write(f)

#         # حفظ فريمات بعد الغش
#         fps = cap.get(cv2.CAP_PROP_FPS) or 20
#         frames_after = int(fps * self.video_after_seconds)
#         for _ in range(frames_after):
#             ret, frame = cap.read()
#             if not ret:
#                 break
#             out.write(frame)

#         out.release()

#         success = self._convert_to_h264(temp_path, full_path)
#         if os.path.exists(temp_path):
#             os.remove(temp_path)
#         if not success:
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
#     # إرسال حالة الغش
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
#             response = requests.post("http://127.0.0.1:8000/cheating-events/", json=data)
#             print(f"📥 رد السيرفر: {response.status_code}")
#             print(f"🚨 حالة غش: {cheating['type_ar']}")

#             self.play_alarm()

#             if self.email_enabled:
#                 self.email_service.send_cheating_alert(
#                     student_name=self.student_name,
#                     student_number=self.student_id,
#                     cheating_type=cheating["type_ar"],
#                     confidence=cheating["confidence"],
#                     snapshot_path=snapshot_full if self.enable_snapshot else None,
#                     video_path=video_full if self.enable_video else None
#                 )
#                 print("📧 تم إرسال الإيميل")

#         except Exception as e:
#             print("❌ خطأ:", e)

#     # =========================
#     # تشغيل النظام
#     # =========================
#     def start_monitoring(self):
#         cap = cv2.VideoCapture(0)  # كاميرا الجهاز — موقوفة
#         # cap = cv2.VideoCapture("rtsp://admin:TVSHZW@192.168.137.32:554/Streaming/Channels/101")

#         if not cap.isOpened():
#             print("❌ لا يمكن فتح الكاميرا")
#             return

#         print("🎥 تم تشغيل الكاميرا")
#         self.audio_service.start()
#         start_time = time.time()

#         fps = cap.get(cv2.CAP_PROP_FPS) or 20
#         self.frame_buffer = deque(maxlen=int(fps * self.video_before_seconds))

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

#                 # =========================
#                 # كشف الغش من ObjectDetectionService
#                 # =========================
#                 detections = self.object_detector.detect_cheating(frame.copy())
#                 cheating_events.extend(detections)

#                 # طباعة تصحيحية لكل كشف
#                 for d in detections:
#                     print(f"[DEBUG] كشف غش: {d['type_ar']} | {d['label']} | {d['confidence']:.2f}")

#                 # كشف حركات الرأس
#                 head = self.head_pose_service.detect_head_pose(frame)
#                 if head:
#                     cheating_events.append(head)

#                 # كشف الصوت
#                 audio = self.audio_service.detect_noise()
#                 if audio:
#                     cheating_events.append(audio)

#                 for cheating in cheating_events:
#                     self.send_cheating_event(cheating, frame.copy(), cap)
#                     cv2.putText(frame, f"Cheating: {cheating['type_ar']}",
#                                 (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

#             cv2.imshow("Exam Monitoring", frame)
#             if cv2.waitKey(1) & 0xFF == 27:  # ESC للخروج
#                 break

#         self.audio_service.stop()
#         cap.release()
#         cv2.destroyAllWindows()
# --------------------------------------
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
        url = "rtsp://admin:TVSHZW@192.168.137.170:554/Streaming/Channels/101"
        
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








# -------------------------------------
# الكود الصح حالي لاخر تحديث كيمرا الجهاز ا
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
# import pymysql  # PyMySQL للاتصال بقاعدة البيانات

# class VideoMonitoringService:
#     def __init__(self):
#         # =========================
#         # خدمات النظام
#         # =========================
#         self.face_service = FaceService()
#         self.object_detector = ObjectDetectionService()
#         self.head_pose_service = HeadPoseService()
#         self.audio_service = AudioService()
#         self.email_service = EmailService()

#         # =========================
#         # بيانات الطالب
#         # =========================
#         self.identity_verified = False
#         self.student_id = None
#         self.student_name = None

#         # =========================
#         # منع التكرار
#         # =========================
#         self.last_cheating_time = {}
#         self.cooldown = 5  # ثواني

#         # =========================
#         # إعدادات النظام الافتراضية
#         # =========================
#         self.video_before_seconds = 3
#         self.video_after_seconds = 7
#         self.email_enabled = True
#         self.enable_video = True
#         self.enable_snapshot = True

#         # =========================
#         # تحميل الإعدادات من قاعدة البيانات
#         # =========================
#         try:
#             conn = pymysql.connect(
#                 host="localhost",
#                 user="root",
#                 password="",
#                 database="exam_monitoring",
#                 charset="utf8mb4",
#                 cursorclass=pymysql.cursors.DictCursor
#             )
#             cursor = conn.cursor()
#             cursor.execute("SELECT setting_key, setting_value FROM settings")
#             settings = cursor.fetchall()
#             for s in settings:
#                 key = s["setting_key"]
#                 value = s["setting_value"]
#                 if key == "video_before_seconds":
#                     self.video_before_seconds = int(value)
#                 elif key == "video_after_seconds":
#                     self.video_after_seconds = int(value)
#                 elif key == "email_enabled":
#                     self.email_enabled = value == "1"
#                 elif key == "save_video":
#                     self.enable_video = value == "1"
#                 elif key == "save_snapshot":
#                     self.enable_snapshot = value == "1"
#             cursor.close()
#             conn.close()
#             print("✅ تم تحميل إعدادات النظام من قاعدة البيانات")
#         except Exception as e:
#             print("⚠ فشل تحميل الإعدادات:", e)

#         # =========================
#         # مجلد الأدلة
#         # =========================
#         self.evidence_dir = "C:/xampp/htdocs/exam_monitoring2/evidence"
#         os.makedirs(self.evidence_dir, exist_ok=True)

#         self.exam_started = False
#         self.frame_buffer = deque()  # سيتم تحديد maxlen بعد معرفة FPS

#     # =========================
#     # حفظ صورة
#     # =========================
#     def save_snapshot(self, frame):
#         if not self.enable_snapshot:
#             return None, None
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
#                 "ffmpeg", "-y",
#                 "-i", input_path,
#                 "-c:v", "libx264",
#                 "-preset", "fast",
#                 "-crf", "23",
#                 "-pix_fmt", "yuv420p",
#                 "-movflags", "+faststart",
#                 "-an",
#                 output_path
#             ]
#             result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
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
#         if not self.enable_video or len(self.frame_buffer) == 0:
#             print("⚠ لن يتم حفظ الفيديو")
#             return None, None

#         timestamp = int(time.time())
#         temp_filename = f"temp_{timestamp}.avi"
#         final_filename = f"video_{timestamp}.mp4"
#         temp_path = os.path.join(self.evidence_dir, temp_filename)
#         full_path = os.path.join(self.evidence_dir, final_filename)

#         height, width, _ = self.frame_buffer[0].shape
#         fourcc = cv2.VideoWriter_fourcc(*"MJPG")
#         out = cv2.VideoWriter(temp_path, fourcc, 20.0, (width, height))

#         if not out.isOpened():
#             print("❌ فشل إنشاء الفيديو المؤقت")
#             return None, None

#         # حفظ فريمات قبل الغش
#         for f in self.frame_buffer:
#             out.write(f)

#         # حفظ فريمات بعد الغش
#         fps = cap.get(cv2.CAP_PROP_FPS) or 20
#         frames_after = int(fps * self.video_after_seconds)
#         for _ in range(frames_after):
#             ret, frame = cap.read()
#             if not ret:
#                 break
#             out.write(frame)

#         out.release()

#         success = self._convert_to_h264(temp_path, full_path)
#         if os.path.exists(temp_path):
#             os.remove(temp_path)
#         if not success:
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
#     # إرسال حالة الغش
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
#             response = requests.post("http://127.0.0.1:8000/cheating-events/", json=data)
#             print(f"📥 رد السيرفر: {response.status_code}")
#             print(f"🚨 حالة غش: {cheating['type_ar']}")

#             self.play_alarm()

#             if self.email_enabled:
#                 self.email_service.send_cheating_alert(
#                     student_name=self.student_name,
#                     student_number=self.student_id,
#                     cheating_type=cheating["type_ar"],
#                     confidence=cheating["confidence"],
#                     snapshot_path=snapshot_full if self.enable_snapshot else None,
#                     video_path=video_full if self.enable_video else None
#                 )
#                 print("📧 تم إرسال الإيميل")

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

#         fps = cap.get(cv2.CAP_PROP_FPS) or 20
#         self.frame_buffer = deque(maxlen=int(fps * self.video_before_seconds))

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
