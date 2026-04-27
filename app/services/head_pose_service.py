# class HeadPoseService:
#     def __init__(self):
#         pass

#     def detect_head_pose(self, frame):  # <-- غيرت الاسم هنا
#         # مؤقتاً نرجع False
#         return False
# ---------------------------------------------------
# هذا الكود الصح
# import cv2
# import numpy as np
# import insightface


# class HeadPoseService:

#     def __init__(self):

#         # تحميل موديل الوجه
#         self.app = insightface.app.FaceAnalysis(name="buffalo_l")
#         self.app.prepare(ctx_id=-1)

#         # حدود الحركة
#         self.yaw_threshold = 30
#         self.pitch_threshold = 25

#     def detect_head_pose(self, frame):

#         try:

#             faces = self.app.get(frame)

#             # إذا لم يوجد وجه
#             if len(faces) == 0:

#                 return {
#                     "cheating_type_id": 7,
#                     "type_ar": "محاولة مغادرة الكاميرا",
#                     "type_en": "Leaving Camera",
#                     "confidence": 0.9
#                 }

#             face = faces[0]

#             # زوايا الرأس
#             yaw = face.pose[0]
#             pitch = face.pose[1]
#             roll = face.pose[2]

#             # النظر بعيد عن الشاشة
#             if abs(yaw) > self.yaw_threshold:

#                 return {
#                     "cheating_type_id": 4,
#                     "type_ar": "النظر بعيداً عن الشاشة",
#                     "type_en": "Looking Away",
#                     "confidence": abs(yaw) / 90
#                 }

#             # حركة رأس غير طبيعية
#             if abs(pitch) > self.pitch_threshold:

#                 return {
#                     "cheating_type_id": 5,
#                     "type_ar": "حركة رأس غير طبيعية",
#                     "type_en": "Abnormal Head Movement",
#                     "confidence": abs(pitch) / 90
#                 }

#             return None

#         except Exception as e:

#             print("Head Pose Error:", e)

#             return None
# --------------------------
# import cv2
# import time
# import insightface
# from collections import defaultdict
# import winsound  # الصوت على Windows

# class HeadPoseService:

#     def __init__(self):

#         self.app = insightface.app.FaceAnalysis(name="buffalo_l")
#         self.app.prepare(ctx_id=-1)

#         # الحدود
#         self.yaw_threshold = 30
#         self.pitch_threshold = 25

#         # الوقت بالثواني
#         self.required_seconds = {
#             "look_away": 0.5,
#             "head_movement": 0.5,
#             "no_face": 0.8
#         }

#         self.start_time = defaultdict(lambda: None)

#         # cooldown
#         self.cooldown = 8
#         self.last_reported = {}

#         print("✅ HeadPose model loaded")

#     # =========================
#     def play_alert(self):
#         try:
#             winsound.Beep(1000, 300)
#             print("🔊 Sound triggered")
#         except:
#             pass

#     # =========================
#     def detect(self, frame):

#         try:
#             faces = self.app.get(frame)
#             detected_types = []

#             now = time.time()

#             # 🚪 لا يوجد وجه
#             if len(faces) == 0:
#                 if self.start_time["no_face"] is None:
#                     self.start_time["no_face"] = now

#                 elif now - self.start_time["no_face"] >= self.required_seconds["no_face"]:
#                     detected_types.append(("no_face", {
#                         "cheating_type_id": 7,
#                         "type_ar": "محاولة مغادرة الكاميرا",
#                         "type_en": "Leaving Camera",
#                         "confidence": 0.9
#                     }))
#             else:
#                 self.start_time["no_face"] = None

#                 face = faces[0]
#                 yaw, pitch, roll = face.pose

#                 cv2.putText(frame, f"Yaw: {yaw:.1f}", (10, 30),
#                             cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
#                 cv2.putText(frame, f"Pitch: {pitch:.1f}", (10, 60),
#                             cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

#                 # 👀 النظر بعيد
#                 if abs(yaw) > self.yaw_threshold:
#                     if self.start_time["look_away"] is None:
#                         self.start_time["look_away"] = now
#                     elif now - self.start_time["look_away"] >= self.required_seconds["look_away"]:
#                         detected_types.append(("look_away", {
#                             "cheating_type_id": 4,
#                             "type_ar": "النظر بعيداً عن الشاشة",
#                             "type_en": "Looking Away",
#                             "confidence": abs(yaw) / 90
#                         }))
#                 else:
#                     self.start_time["look_away"] = None

#                 # 👇 حركة غير طبيعية
#                 if abs(pitch) > self.pitch_threshold:
#                     if self.start_time["head_movement"] is None:
#                         self.start_time["head_movement"] = now
#                     elif now - self.start_time["head_movement"] >= self.required_seconds["head_movement"]:
#                         detected_types.append(("head_movement", {
#                             "cheating_type_id": 5,
#                             "type_ar": "حركة رأس غير طبيعية",
#                             "type_en": "Abnormal Head Movement",
#                             "confidence": abs(pitch) / 90
#                         }))
#                 else:
#                     self.start_time["head_movement"] = None

#             # =========================
#             # cooldown
#             # =========================
#             final_detections = []

#             for key, data in detected_types:
#                 last = self.last_reported.get(key, 0)
#                 if now - last >= self.cooldown:
#                     self.last_reported[key] = now
#                     final_detections.append(data)
#                     self.play_alert()

#             return final_detections

#         except Exception as e:
#             print("Head Pose Error:", e)
#             return []

#     # =========================
#     def detect_cheating(self, frame):
#         return self.detect(frame)

#     # ✅ الحل الأول (لحل الخطأ)
#     def detect_head_pose(self, frame):
#         return self.detect(frame)


# # =========================
# # تشغيل مستقل
# # =========================
# if __name__ == "__main__":

#     detector = HeadPoseService()
#     cap = cv2.VideoCapture(0)

#     print("🎥 Camera started... Press ESC to exit")

#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             break

#         detections = detector.detect_cheating(frame)

#         for d in detections:
#             print(f"🚨 {d['type_ar']} | {d['confidence']:.2f}")
#             cv2.putText(frame, d["type_ar"], (10, 100),
#                         cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

#         cv2.imshow("Head Pose Test", frame)

#         if cv2.waitKey(1) & 0xFF == 27:
#             break

#     cap.release()
#     cv2.destroyAllWindows()
# ------------------------------------
# الصح
# import cv2
# import time
# import insightface
# from collections import defaultdict
# import winsound  # الصوت على Windows

# class HeadPoseService:

#     def __init__(self):

#         self.app = insightface.app.FaceAnalysis(name="buffalo_l")
#         self.app.prepare(ctx_id=-1)

#         # الحدود
#         self.yaw_threshold = 30   # التفت يمين/يسار
#         self.pitch_threshold = 25 # حركة رأس للأعلى/الأسفل

#         # الوقت بالثواني لتحديد الغش
#         self.required_seconds = {
#             "look_away": 0.5,       # التفت أكثر من 0.5 ثانية
#             "head_movement": 0.5,   # حركة رأس غير طبيعية أكثر من 0.5 ثانية
#             "no_face": 0.8           # لا يوجد وجه (سنوقف استخدامها للحظي)
#         }

#         # وقت بدء الحالة
#         self.start_time = defaultdict(lambda: None)

#         # منع التكرار
#         self.cooldown = 8  # ثواني
#         self.last_reported = {}

#         print("✅ HeadPose model loaded")

#     # =========================
#     def play_alert(self):
#         try:
#             winsound.Beep(1000, 300)  # تردد + مدة
#             print("🔊 Sound triggered")
#         except:
#             pass

#     # =========================
#     def detect(self, frame):

#         try:
#             faces = self.app.get(frame)
#             detected_types = []

#             now = time.time()

#             # 🚪 لا يوجد وجه --> معلق، لن يتم إصدار صوت أو طباعة
#             if len(faces) == 0:
#                 # إذا أحببت، يمكن تسجيل الوقت هنا لحفظه لاحقًا مع الفيديو الكامل
#                 self.start_time["no_face"] = now  # فقط للتسجيل، لا غش لحظي
#             else:
#                 self.start_time["no_face"] = None  # إعادة تعيين عند ظهور الوجه

#                 face = faces[0]
#                 yaw, pitch, roll = face.pose

#                 # عرض القيم على الفيديو
#                 cv2.putText(frame, f"Yaw: {yaw:.1f}", (10, 30),
#                             cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
#                 cv2.putText(frame, f"Pitch: {pitch:.1f}", (10, 60),
#                             cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

#                 # 👀 النظر بعيد
#                 if abs(yaw) > self.yaw_threshold:
#                     if self.start_time["look_away"] is None:
#                         self.start_time["look_away"] = now
#                     elif now - self.start_time["look_away"] >= self.required_seconds["look_away"]:
#                         detected_types.append(("look_away", {
#                             "cheating_type_id": 4,
#                             "type_ar": "النظر بعيداً عن الشاشة",
#                             "type_en": "Looking Away",
#                             "confidence": abs(yaw) / 90
#                         }))
#                 else:
#                     self.start_time["look_away"] = None

#                 # 👇 حركة غير طبيعية
#                 if abs(pitch) > self.pitch_threshold:
#                     if self.start_time["head_movement"] is None:
#                         self.start_time["head_movement"] = now
#                     elif now - self.start_time["head_movement"] >= self.required_seconds["head_movement"]:
#                         detected_types.append(("head_movement", {
#                             "cheating_type_id": 5,
#                             "type_ar": "حركة رأس غير طبيعية",
#                             "type_en": "Abnormal Head Movement",
#                             "confidence": abs(pitch) / 90
#                         }))
#                 else:
#                     self.start_time["head_movement"] = None

#             # =========================
#             # تطبيق cooldown + منع التكرار
#             # =========================
#             final_detections = []

#             for key, data in detected_types:
#                 last = self.last_reported.get(key, 0)
#                 if now - last >= self.cooldown:
#                     self.last_reported[key] = now
#                     final_detections.append(data)
#                     self.play_alert()

#             return final_detections

#         except Exception as e:
#             print("Head Pose Error:", e)
#             return []

#     # =========================
#     def detect_cheating(self, frame):
#         return self.detect(frame)


# # =========================
# # تشغيل مستقل
# # =========================
# if __name__ == "__main__":

#     detector = HeadPoseService()
#     cap = cv2.VideoCapture(0)

#     print("🎥 Camera started... Press ESC to exit")

#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             break

#         detections = detector.detect_cheating(frame)

#         for d in detections:
#             print(f"🚨 {d['type_ar']} | {d['confidence']:.2f}")
#             cv2.putText(frame, d["type_ar"], (10, 100),
#                         cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

#         cv2.imshow("Head Pose Test", frame)

#         if cv2.waitKey(1) & 0xFF == 27:
#             break

#     cap.release()
#     cv2.destroyAllWindows()
# ------------------------------------
# import cv2
# import time
# import os
# import insightface
# from collections import defaultdict
# import winsound  # الصوت على Windows

# class HeadPoseService:

#     def __init__(self):

#         # 🔹 تحميل موديل الوجه
#         self.app = insightface.app.FaceAnalysis(name="buffalo_l")
#         self.app.prepare(ctx_id=-1)

#         # 🔹 حدود الحركة
#         self.yaw_threshold = 30   # التفت يمين/يسار
#         self.pitch_threshold = 25 # حركة رأس للأعلى/الأسفل

#         # ⏱️ الوقت بالثواني لتحديد الغش
#         self.required_seconds = {
#             "look_away": 0.5,
#             "head_movement": 0.5,
#             "no_face": 5  # وجه مختفي أكثر من 5 ثواني = غش
#         }

#         # ⏱️ وقت بدء الحالة
#         self.start_time = defaultdict(lambda: None)

#         # ⛔ منع التكرار
#         self.cooldown = 8  # ثواني
#         self.last_reported = {}

#         print("✅ HeadPose model loaded")

#     # =========================
#     # 🔊 إصدار صوت تنبيه
#     def play_alert(self):
#         try:
#             winsound.Beep(1000, 300)  # تردد + مدة
#             print("🔊 Sound triggered")
#         except:
#             pass

#     # =========================
#     # كشف حالات الغش
#     def detect_head_pose(self, frame):
#         try:
#             faces = self.app.get(frame)
#             now = time.time()

#             # =========================
#             # 🚪 لا يوجد وجه
#             # =========================
#             if len(faces) == 0:
#                 if self.start_time["no_face"] is None:
#                     self.start_time["no_face"] = now

#                 elif now - self.start_time["no_face"] >= self.required_seconds["no_face"]:
#                     last = self.last_reported.get("no_face", 0)
#                     if now - last >= self.cooldown:
#                         self.last_reported["no_face"] = now
#                         self.play_alert()
#                         return {
#                             "cheating_type_id": 7,
#                             "type_ar": "محاولة مغادرة الكاميرا",
#                             "type_en": "Leaving Camera",
#                             "confidence": 0.9
#                         }
#                 return None
#             else:
#                 self.start_time["no_face"] = None  # إعادة التعيين عند ظهور الوجه

#             face = faces[0]
#             yaw, pitch, roll = face.pose

#             # عرض القيم على الفيديو
#             cv2.putText(frame, f"Yaw: {yaw:.1f}", (10, 30),
#                         cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
#             cv2.putText(frame, f"Pitch: {pitch:.1f}", (10, 60),
#                         cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

#             # =========================
#             # 👀 النظر بعيد عن الشاشة
#             # =========================
#             if abs(yaw) > self.yaw_threshold:
#                 if self.start_time["look_away"] is None:
#                     self.start_time["look_away"] = now
#                 elif now - self.start_time["look_away"] >= self.required_seconds["look_away"]:
#                     last = self.last_reported.get("look_away", 0)
#                     if now - last >= self.cooldown:
#                         self.last_reported["look_away"] = now
#                         self.play_alert()
#                         return {
#                             "cheating_type_id": 4,
#                             "type_ar": "النظر بعيداً عن الشاشة",
#                             "type_en": "Looking Away",
#                             "confidence": abs(yaw) / 90
#                         }
#             else:
#                 self.start_time["look_away"] = None

#             # =========================
#             # 👇 حركة رأس غير طبيعية
#             # =========================
#             if abs(pitch) > self.pitch_threshold:
#                 if self.start_time["head_movement"] is None:
#                     self.start_time["head_movement"] = now
#                 elif now - self.start_time["head_movement"] >= self.required_seconds["head_movement"]:
#                     last = self.last_reported.get("head_movement", 0)
#                     if now - last >= self.cooldown:
#                         self.last_reported["head_movement"] = now
#                         self.play_alert()
#                         return {
#                             "cheating_type_id": 5,
#                             "type_ar": "حركة رأس غير طبيعية",
#                             "type_en": "Abnormal Head Movement",
#                             "confidence": abs(pitch) / 90
#                         }
#             else:
#                 self.start_time["head_movement"] = None

#             return None

#         except Exception as e:
#             print("Head Pose Error:", e)
#             return None


# # =========================
# # 🔹 تشغيل مستقل
# # =========================
# if __name__ == "__main__":

#     # الكاميرا الخارجية — Stream الثاني 30 FPS @ 640x480 (أخف وأسرع)
#     RTSP_URL = "rtsp://admin:TVSHZW@192.168.137.32:554/Streaming/Channels/102"
#     # Stream الأول 1080p @ 12.5 FPS — ثقيل، موقوف
#     # RTSP_URL = "rtsp://admin:TVSHZW@192.168.137.32:554/Streaming/Channels/101"
#     # كاميرا الجهاز موقوفة
#     # cap = cv2.VideoCapture(0)

#     detector = HeadPoseService()

#     os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp|loglevel;quiet"
#     cap = cv2.VideoCapture(RTSP_URL, cv2.CAP_FFMPEG)
#     cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)

#     if not cap.isOpened():
#         print("❌ فشل الاتصال بالكاميرا")
#         exit()

#     fps = cap.get(cv2.CAP_PROP_FPS) or 30
#     print(f"🎥 Camera started | FPS: {fps} | Press ESC to exit")

#     fail_count = 0

#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             fail_count += 1
#             if fail_count > 10:
#                 print("❌ انقطع الاتصال، إعادة الاتصال...")
#                 cap.release()
#                 time.sleep(2)
#                 cap = cv2.VideoCapture(RTSP_URL, cv2.CAP_FFMPEG)
#                 cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)
#                 fail_count = 0
#             continue

#         fail_count = 0  # إعادة العداد عند نجاح القراءة

#         cheating = detector.detect_head_pose(frame)

#         if cheating:
#             print(f"🚨 {cheating['type_ar']} | {cheating['confidence']:.2f}")
#             cv2.putText(frame, cheating["type_ar"], (10, 100),
#                         cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

#         cv2.imshow("Head Pose Test", frame)

#         if cv2.waitKey(1) & 0xFF == 27:
#             break

#     cap.release()
#     cv2.destroyAllWindows()
# ----------------------------------
# كود الكيمرا 
import cv2
import time
import insightface
from collections import defaultdict
import winsound
import threading

# =========================
# Threaded Video Capture لتجنب تعليق الفيديو
class VideoStream:
    def __init__(self, url):
        self.cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.ret, self.frame = self.cap.read()
        self.running = True
        self.thread = threading.Thread(target=self.update, daemon=True)
        self.thread.start()

    def update(self):
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                self.ret = ret
                self.frame = frame

    def read(self):
        return self.ret, self.frame

    def stop(self):
        self.running = False
        self.thread.join()
        self.cap.release()


# =========================
# كشف حركة الرأس
class HeadPoseService:

    def __init__(self):
        self.app = insightface.app.FaceAnalysis(name="buffalo_l")
        self.app.prepare(ctx_id=-1)

        self.yaw_threshold = 30
        self.pitch_threshold = 25

        self.required_seconds = {
            "look_away": 0.5,
            "head_movement": 0.5,
            "no_face": 5
        }

        self.start_time = defaultdict(lambda: None)
        self.cooldown = 5
        self.last_reported = {}
        print("✅ HeadPose model loaded")

    def play_alert(self):
        try:
            winsound.Beep(1000, 300)
        except:
            pass

    def detect_head_pose(self, frame):
        try:
            faces = self.app.get(frame)
            now = time.time()

            # 🚪 لا يوجد وجه
            if len(faces) == 0:
                if self.start_time["no_face"] is None:
                    self.start_time["no_face"] = now
                elif now - self.start_time["no_face"] >= self.required_seconds["no_face"]:
                    last = self.last_reported.get("no_face", 0)
                    if now - last >= self.cooldown:
                        self.last_reported["no_face"] = now
                        self.play_alert()
                        return {
                            "cheating_type_id": 7,
                            "type_ar": "محاولة مغادرة الكاميرا",
                            "type_en": "Leaving Camera",
                            "confidence": 0.9
                        }
                return None
            else:
                self.start_time["no_face"] = None

            face = faces[0]
            yaw, pitch, roll = face.pose

            cv2.putText(frame, f"Yaw: {yaw:.1f}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(frame, f"Pitch: {pitch:.1f}", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            # 👀 النظر بعيد عن الشاشة
            if abs(yaw) > self.yaw_threshold:
                if self.start_time["look_away"] is None:
                    self.start_time["look_away"] = now
                elif now - self.start_time["look_away"] >= self.required_seconds["look_away"]:
                    last = self.last_reported.get("look_away", 0)
                    if now - last >= self.cooldown:
                        self.last_reported["look_away"] = now
                        self.play_alert()
                        return {
                            "cheating_type_id": 4,
                            "type_ar": "النظر بعيداً عن الشاشة",
                            "type_en": "Looking Away",
                            "confidence": abs(yaw) / 90
                        }
            else:
                self.start_time["look_away"] = None

            # 👇 حركة رأس غير طبيعية
            if abs(pitch) > self.pitch_threshold:
                if self.start_time["head_movement"] is None:
                    self.start_time["head_movement"] = now
                elif now - self.start_time["head_movement"] >= self.required_seconds["head_movement"]:
                    last = self.last_reported.get("head_movement", 0)
                    if now - last >= self.cooldown:
                        self.last_reported["head_movement"] = now
                        self.play_alert()
                        return {
                            "cheating_type_id": 5,
                            "type_ar": "حركة رأس غير طبيعية",
                            "type_en": "Abnormal Head Movement",
                            "confidence": abs(pitch) / 90
                        }
            else:
                self.start_time["head_movement"] = None

            return None

        except Exception as e:
            print("Head Pose Error:", e)
            return None


# =========================
# تشغيل مستقل
if __name__ == "__main__":
    url = "rtsp://admin:TVSHZW@192.168.137.225:554/Streaming/Channels/101"
    stream = VideoStream(url)
    time.sleep(2)

    detector = HeadPoseService()

    print("🎥 Camera started... Press ESC to exit")

    while True:
        ret, frame = stream.read()
        if not ret or frame is None:
            continue

        frame = cv2.resize(frame, (480, 360))

        cheating = detector.detect_head_pose(frame)

        if cheating:
            print(f"🚨 {cheating['type_ar']} | {cheating.get('confidence', 0):.2f}")
            cv2.putText(frame, cheating["type_ar"], (10, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        cv2.imshow("Head Pose Camera", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    stream.stop()
    cv2.destroyAllWindows()
# ----------------------------------
# حاليا الصح
# import cv2
# import time
# import insightface
# from collections import defaultdict
# import winsound  # الصوت على Windows


# class HeadPoseService:

#     def __init__(self):

#         # 🔹 تحميل موديل الوجه
#         self.app = insightface.app.FaceAnalysis(name="buffalo_l")
#         self.app.prepare(ctx_id=-1)

#         # 🔹 حدود الحركة
#         self.yaw_threshold = 30   # التفت يمين/يسار
#         self.pitch_threshold = 25 # حركة رأس للأعلى/الأسفل

#         # ⏱️ الوقت بالثواني لتحديد الغش
#         self.required_seconds = {
#             "look_away": 0.8,
#             "head_movement": 0.8,
#             "no_face": 5  # وجه مختفي أكثر من 5 ثواني = غش
#         }

#         # ⏱️ وقت بدء الحالة
#         self.start_time = defaultdict(lambda: None)

#         # ⛔ منع التكرار
#         self.cooldown = 8  # ثواني
#         self.last_reported = {}

#         print("✅ HeadPose model loaded")

#     # =========================
#     # 🔊 إصدار صوت تنبيه
#     def play_alert(self):
#         try:
#             winsound.Beep(1000, 300)  # تردد + مدة
#             print("🔊 Sound triggered")
#         except:
#             pass

#     # =========================
#     # كشف حالات الغش
#     def detect_head_pose(self, frame):
#         try:
#             faces = self.app.get(frame)
#             now = time.time()

#             # =========================
#             # 🚪 لا يوجد وجه
#             # =========================
#             if len(faces) == 0:
#                 if self.start_time["no_face"] is None:
#                     self.start_time["no_face"] = now

#                 elif now - self.start_time["no_face"] >= self.required_seconds["no_face"]:
#                     last = self.last_reported.get("no_face", 0)
#                     if now - last >= self.cooldown:
#                         self.last_reported["no_face"] = now
#                         self.play_alert()
#                         return {
#                             "cheating_type_id": 7,
#                             "type_ar": "محاولة مغادرة الكاميرا",
#                             "type_en": "Leaving Camera",
#                             "confidence": 0.9
#                         }
#                 return None
#             else:
#                 self.start_time["no_face"] = None  # إعادة التعيين عند ظهور الوجه

#             face = faces[0]
#             yaw, pitch, roll = face.pose

#             # عرض القيم على الفيديو
#             cv2.putText(frame, f"Yaw: {yaw:.1f}", (10, 30),
#                         cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
#             cv2.putText(frame, f"Pitch: {pitch:.1f}", (10, 60),
#                         cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

#             # =========================
#             # 👀 النظر بعيد عن الشاشة
#             # =========================
#             if abs(yaw) > self.yaw_threshold:
#                 if self.start_time["look_away"] is None:
#                     self.start_time["look_away"] = now
#                 elif now - self.start_time["look_away"] >= self.required_seconds["look_away"]:
#                     last = self.last_reported.get("look_away", 0)
#                     if now - last >= self.cooldown:
#                         self.last_reported["look_away"] = now
#                         self.play_alert()
#                         return {
#                             "cheating_type_id": 4,
#                             "type_ar": "النظر بعيداً عن الشاشة",
#                             "type_en": "Looking Away",
#                             "confidence": abs(yaw) / 90
#                         }
#             else:
#                 self.start_time["look_away"] = None

#             # =========================
#             # 👇 حركة رأس غير طبيعية
#             # =========================
#             if abs(pitch) > self.pitch_threshold:
#                 if self.start_time["head_movement"] is None:
#                     self.start_time["head_movement"] = now
#                 elif now - self.start_time["head_movement"] >= self.required_seconds["head_movement"]:
#                     last = self.last_reported.get("head_movement", 0)
#                     if now - last >= self.cooldown:
#                         self.last_reported["head_movement"] = now
#                         self.play_alert()
#                         return {
#                             "cheating_type_id": 5,
#                             "type_ar": "حركة رأس غير طبيعية",
#                             "type_en": "Abnormal Head Movement",
#                             "confidence": abs(pitch) / 90
#                         }
#             else:
#                 self.start_time["head_movement"] = None

#             return None

#         except Exception as e:
#             print("Head Pose Error:", e)
#             return None


# # =========================
# # 🔹 تشغيل مستقل
# # =========================
# if __name__ == "__main__":

#     detector = HeadPoseService()
#     cap = cv2.VideoCapture(0)

#     print("🎥 Camera started... Press ESC to exit")

#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             break

#         cheating = detector.detect_head_pose(frame)

#         if cheating:
#             print(f"🚨 {cheating['type_ar']} | {cheating['confidence']:.2f}")
#             cv2.putText(frame, cheating["type_ar"], (10, 100),
#                         cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

#         cv2.imshow("Head Pose Test", frame)

#         if cv2.waitKey(1) & 0xFF == 27:
#             break

#     cap.release()
#     cv2.destroyAllWindows()
# ---------------------------------



