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
#         self.eye_yaw_threshold = 15  # زاوية العين للكشف عن النظر بعيدًا
#         self.eye_pitch_threshold = 10

#         # ⏱️ الوقت بالثواني لتحديد الغش
#         self.required_seconds = {
#             "look_away": 0.5,
#             "head_movement": 0.5,
#             "no_face": 5,     # وجه مختفي أكثر من 5 ثواني = غش
#             "eye_look_away": 1 # العين بعيد عن الشاشة أكثر من 1 ثانية
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
#             # 👀 النظر بعيد عن الشاشة (الرأس)
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

#             # =========================
#             # 👁️ مراقبة العين (حالة رقم 8)
#             # إذا الرأس ثابت والجسم ثابت لكن العين تنظر بعيد
#             # =========================
#             if abs(yaw) <= self.yaw_threshold and abs(pitch) <= self.pitch_threshold:
#                 # زاوية العين صغيرة لكن بعيدة عن المركز
#                 eye_yaw, eye_pitch = face.kps[0][0]-face.kps[1][0], face.kps[0][1]-face.kps[1][1]  # تبسيط: الفرق بين نقطتين للعين
#                 if abs(eye_yaw) > self.eye_yaw_threshold or abs(eye_pitch) > self.eye_pitch_threshold:
#                     if self.start_time["eye_look_away"] is None:
#                         self.start_time["eye_look_away"] = now
#                     elif now - self.start_time["eye_look_away"] >= self.required_seconds["eye_look_away"]:
#                         last = self.last_reported.get("eye_look_away", 0)
#                         if now - last >= self.cooldown:
#                             self.last_reported["eye_look_away"] = now
#                             self.play_alert()
#                             return {
#                                 "cheating_type_id": 8,
#                                 "type_ar": "مراقبة العين بعيداً عن الشاشة",
#                                 "type_en": "Eye Looking Away",
#                                 "confidence": max(abs(eye_yaw)/20, abs(eye_pitch)/20)
#                             }
#                 else:
#                     self.start_time["eye_look_away"] = None

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
# ----------------------------------
# حاليا الصح
import cv2
import time
import insightface
from collections import defaultdict
import winsound  # الصوت على Windows


class HeadPoseService:

    def __init__(self):

        # 🔹 تحميل موديل الوجه
        self.app = insightface.app.FaceAnalysis(name="buffalo_l")
        self.app.prepare(ctx_id=-1)

        # 🔹 حدود الحركة
        self.yaw_threshold = 30   # التفت يمين/يسار
        self.pitch_threshold = 25 # حركة رأس للأعلى/الأسفل

        # ⏱️ الوقت بالثواني لتحديد الغش
        self.required_seconds = {
            "look_away": 0.5,
            "head_movement": 0.5,
            "no_face": 5  # وجه مختفي أكثر من 5 ثواني = غش
        }

        # ⏱️ وقت بدء الحالة
        self.start_time = defaultdict(lambda: None)

        # ⛔ منع التكرار
        self.cooldown = 8  # ثواني
        self.last_reported = {}

        print("✅ HeadPose model loaded")

    # =========================
    # 🔊 إصدار صوت تنبيه
    def play_alert(self):
        try:
            winsound.Beep(1000, 300)  # تردد + مدة
            print("🔊 Sound triggered")
        except:
            pass

    # =========================
    # كشف حالات الغش
    def detect_head_pose(self, frame):
        try:
            faces = self.app.get(frame)
            now = time.time()

            # =========================
            # 🚪 لا يوجد وجه
            # =========================
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
                self.start_time["no_face"] = None  # إعادة التعيين عند ظهور الوجه

            face = faces[0]
            yaw, pitch, roll = face.pose

            # عرض القيم على الفيديو
            cv2.putText(frame, f"Yaw: {yaw:.1f}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(frame, f"Pitch: {pitch:.1f}", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            # =========================
            # 👀 النظر بعيد عن الشاشة
            # =========================
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

            # =========================
            # 👇 حركة رأس غير طبيعية
            # =========================
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
# 🔹 تشغيل مستقل
# =========================
if __name__ == "__main__":

    detector = HeadPoseService()
    cap = cv2.VideoCapture(0)

    print("🎥 Camera started... Press ESC to exit")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        cheating = detector.detect_head_pose(frame)

        if cheating:
            print(f"🚨 {cheating['type_ar']} | {cheating['confidence']:.2f}")
            cv2.putText(frame, cheating["type_ar"], (10, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        cv2.imshow("Head Pose Test", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
# ---------------------------------
# import cv2
# import time
# import mediapipe as mp
# import insightface
# from collections import defaultdict, deque
# import winsound
# import numpy as np

# class HeadPoseService:
#     def __init__(self):
#         # insightface للرأس
#         self.app = insightface.app.FaceAnalysis(name="buffalo_l")
#         self.app.prepare(ctx_id=-1)

#         # MediaPipe للعين
#         self.mp_face_mesh = mp.solutions.face_mesh
#         self.face_mesh = self.mp_face_mesh.FaceMesh(
#             max_num_faces=1,
#             refine_landmarks=True,  # مهم: يفعّل نقاط القزحية
#             min_detection_confidence=0.5,
#             min_tracking_confidence=0.5
#         )

#         self.yaw_threshold = 30
#         self.pitch_threshold = 25

#         self.required_seconds = {
#             "look_away": 0.5,
#             "head_movement": 0.5,
#             "no_face": 5,
#             "eye_look_away": 1.5
#         }

#         self.start_time = defaultdict(lambda: None)
#         self.cooldown = 8
#         self.last_reported = {}

#         # تاريخ نسبة العين لكشف الحركة المتكررة
#         self.iris_history = deque(maxlen=20)

#         print("✅ HeadPose + MediaPipe loaded")

#     def play_alert(self):
#         try:
#             winsound.Beep(1000, 300)
#         except:
#             pass

#     def _get_iris_ratio(self, landmarks, w, h):
#         """
#         حساب موضع القزحية نسبةً لعرض العين.
#         نقاط العين اليسرى: 33=يمين العين, 133=يسار العين, 468=مركز القزحية
#         القيمة: 0.0 = ينظر يمين، 0.5 = مركز، 1.0 = ينظر يسار
#         """
#         # العين اليسرى
#         left_corner  = landmarks[33]
#         right_corner = landmarks[133]
#         iris_center  = landmarks[468]  # يتطلب refine_landmarks=True

#         eye_width = abs(right_corner.x - left_corner.x)
#         if eye_width < 0.001:
#             return 0.5

#         iris_ratio = (iris_center.x - left_corner.x) / eye_width
#         return iris_ratio

#     def _check_eye_looking_away(self, frame):
#         """
#         يرجع True إذا كانت العين تنظر بعيداً بشكل مستمر عبر الفريمات.
#         """
#         rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         results = self.face_mesh.process(rgb)

#         if not results.multi_face_landmarks:
#             return False

#         landmarks = results.multi_face_landmarks[0].landmark
#         ratio = self._get_iris_ratio(landmarks, frame.shape[1], frame.shape[0])
#         self.iris_history.append(ratio)

#         if len(self.iris_history) < 10:
#             return False

#         avg_ratio = np.mean(self.iris_history)
#         # 0.5 = مركز، إذا انحرف عن المركز بأكثر من 0.15 = ينظر بعيد
#         deviation = abs(avg_ratio - 0.5)
#         return deviation > 0.15

#     def detect_head_pose(self, frame):
#         try:
#             faces = self.app.get(frame)
#             now = time.time()

#             # 🚪 لا يوجد وجه
#             if len(faces) == 0:
#                 self.iris_history.clear()
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
#                 self.start_time["no_face"] = None

#             face = faces[0]
#             yaw, pitch, roll = face.pose

#             cv2.putText(frame, f"Yaw: {yaw:.1f}", (10, 30),
#                         cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
#             cv2.putText(frame, f"Pitch: {pitch:.1f}", (10, 60),
#                         cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

#             # 👀 النظر بعيد (الرأس)
#             if abs(yaw) > self.yaw_threshold:
#                 self.iris_history.clear()
#                 self.start_time["eye_look_away"] = None
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

#             # 👇 حركة رأس غير طبيعية
#             if abs(pitch) > self.pitch_threshold:
#                 self.iris_history.clear()
#                 self.start_time["eye_look_away"] = None
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

#             # 👁️ مراقبة العين عبر MediaPipe (الرأس ثابت)
#             if abs(yaw) <= self.yaw_threshold and abs(pitch) <= self.pitch_threshold:
#                 if self._check_eye_looking_away(frame):
#                     if self.start_time["eye_look_away"] is None:
#                         self.start_time["eye_look_away"] = now
#                     elif now - self.start_time["eye_look_away"] >= self.required_seconds["eye_look_away"]:
#                         last = self.last_reported.get("eye_look_away", 0)
#                         if now - last >= self.cooldown:
#                             self.last_reported["eye_look_away"] = now
#                             self.play_alert()
#                             return {
#                                 "cheating_type_id": 8,
#                                 "type_ar": "مراقبة العين بعيداً عن الشاشة",
#                                 "type_en": "Eye Looking Away",
#                                 "confidence": 0.85
#                             }
#                 else:
#                     self.start_time["eye_look_away"] = None

#             return None

#         except Exception as e:
#             print("Head Pose Error:", e)
#             return None


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

