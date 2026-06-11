import cv2
import numpy as np
import time
import insightface
from collections import defaultdict
import winsound


class HeadPoseService:

    def __init__(self):

        # 🔹 تحميل موديل الوجه
        self.app = insightface.app.FaceAnalysis(name="buffalo_l")
        self.app.prepare(ctx_id=-1, det_size=(320, 320))

        # 🔹 حدود الحركة
        self.yaw_threshold = 30
        self.pitch_threshold = 25

        # ⏱️ الوقت بالثواني لتحديد الغش
        self.required_seconds = {
            "look_away": 0.5,
            "head_movement": 0.3,
            "no_face": 1
        }

        self.start_time = defaultdict(lambda: None)

        # ⛔ منع التكرار
        self.cooldown = 5
        self.last_reported = {}

        # ✅ تتبع الطلاب المتوقعين
        self.expected_students = []
        self.student_absent_since = {}

        print("✅ HeadPose model loaded")

    # =========================
    # 🔊 إصدار صوت تنبيه
    # =========================
    def play_alert(self):
        try:
            winsound.Beep(1000, 300)
            print("🔊 Sound triggered")
        except:
            pass

    # =========================
    # ✅ تعيين الطلاب المتوقعين من video_service
    # =========================
    def set_expected_students(self, students):
        self.expected_students = students
        self.student_absent_since = {}
        print(f"✅ HeadPose: تم تعيين {len(students)} طلاب متوقعين")

    # =========================
    # ✅ مطابقة وجه مع قائمة الطلاب
    # =========================
    def _match_face_to_student(self, face_embedding):
        if not self.expected_students:
            return None

        emb = face_embedding.astype(np.float32)
        emb = emb / (np.linalg.norm(emb) + 1e-8)

        best_sim = 0.5
        best_student = None

        for student in self.expected_students:
            if not student.get("embedding"):
                continue
            stored = np.frombuffer(student["embedding"], dtype=np.float32)
            stored = stored / (np.linalg.norm(stored) + 1e-8)
            sim = float(np.dot(emb, stored))
            if sim > best_sim:
                best_sim = sim
                best_student = student

        return best_student

    # =========================
    # كشف حالات الغش
    # =========================
    def detect_head_pose(self, frame):
        try:
            # تصغير الفريم لتسريع المعالجة
            height, width = frame.shape[:2]
            if width > 640:
                scale = 640 / width
                new_width = 640
                new_height = int(height * scale)
                frame_small = cv2.resize(frame, (new_width, new_height))
            else:
                frame_small = frame

            faces = self.app.get(frame_small)
            now = time.time()
            all_cheatings = []

            # =========================
            # ✅ كشف الطلاب الغائبين بشكل مستقل
            # =========================
            if self.expected_students:
                # حدد أي الطلاب موجودون الآن
                present_student_ids = set()
                for face in faces:
                    matched = self._match_face_to_student(face.embedding)
                    if matched:
                        present_student_ids.add(matched["student_id"])

                # فحص كل طالب متوقع
                for student in self.expected_students:
                    sid = student["student_id"]
                    sname = student["student_name"]

                    if sid not in present_student_ids:
                        # الطالب غائب - ابدأ العد
                        if sid not in self.student_absent_since:
                            self.student_absent_since[sid] = now
                            print(f"⚠️ الطالب {sname} اختفى من الكاميرا")
                        elif now - self.student_absent_since[sid] >= self.required_seconds["no_face"]:
                            key = f"no_face_{sid}"
                            last = self.last_reported.get(key, 0)
                            if now - last >= self.cooldown:
                                self.last_reported[key] = now
                                self.play_alert()
                                all_cheatings.append({
                                    "cheating_type_id": 7,
                                    "type_ar": "محاولة مغادرة الكاميرا",
                                    "type_en": "Leaving Camera",
                                    "confidence": 0.9,
                                    "face_embedding": student["embedding"]
                                })
                                print(f"🚨 تم تسجيل غياب الطالب: {sname}")
                    else:
                        # الطالب موجود - إعادة تعيين
                        if sid in self.student_absent_since:
                            del self.student_absent_since[sid]

            else:
                # =========================
                # fallback: لا يوجد طلاب محددون
                # =========================
                if len(faces) == 0:
                    if self.start_time["no_face"] is None:
                        self.start_time["no_face"] = now
                    elif now - self.start_time["no_face"] >= self.required_seconds["no_face"]:
                        last = self.last_reported.get("no_face", 0)
                        if now - last >= self.cooldown:
                            self.last_reported["no_face"] = now
                            self.play_alert()
                            return [{
                                "cheating_type_id": 7,
                                "type_ar": "محاولة مغادرة الكاميرا",
                                "type_en": "Leaving Camera",
                                "confidence": 0.9
                            }]
                    return []
                else:
                    self.start_time["no_face"] = None

            # =========================
            # فحص حركة الرأس لكل وجه موجود
            # =========================
            for idx, face in enumerate(faces):
                yaw, pitch, roll = face.pose

                if idx == 0:
                    cv2.putText(frame, f"Yaw: {yaw:.1f}", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    cv2.putText(frame, f"Pitch: {pitch:.1f}", (10, 60),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                # 👀 النظر بعيد عن الشاشة
                if abs(yaw) > self.yaw_threshold:
                    key = f"look_away_{idx}"
                    if self.start_time[key] is None:
                        self.start_time[key] = now
                    elif now - self.start_time[key] >= self.required_seconds["look_away"]:
                        last = self.last_reported.get(key, 0)
                        if now - last >= self.cooldown:
                            self.last_reported[key] = now
                            self.play_alert()
                            all_cheatings.append({
                                "cheating_type_id": 4,
                                "type_ar": "النظر بعيداً عن الشاشة",
                                "type_en": "Looking Away",
                                "confidence": abs(yaw) / 90,
                                "face_embedding": face.embedding.astype(np.float32).tobytes()
                            })
                else:
                    key = f"look_away_{idx}"
                    self.start_time[key] = None

                # 👇 حركة رأس غير طبيعية
                if abs(pitch) > self.pitch_threshold:
                    key = f"head_movement_{idx}"
                    if self.start_time[key] is None:
                        self.start_time[key] = now
                    elif now - self.start_time[key] >= self.required_seconds["head_movement"]:
                        last = self.last_reported.get(key, 0)
                        if now - last >= self.cooldown:
                            self.last_reported[key] = now
                            self.play_alert()
                            all_cheatings.append({
                                "cheating_type_id": 5,
                                "type_ar": "حركة رأس غير طبيعية",
                                "type_en": "Abnormal Head Movement",
                                "confidence": abs(pitch) / 90,
                                "face_embedding": face.embedding.astype(np.float32).tobytes()
                            })
                else:
                    key = f"head_movement_{idx}"
                    self.start_time[key] = None

            return all_cheatings

        except Exception as e:
            print("Head Pose Error:", e)
            return []


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

        cheatings = detector.detect_head_pose(frame)

        for cheating in cheatings:
            print(f"🚨 {cheating['type_ar']} | {cheating['confidence']:.2f}")
            cv2.putText(frame, cheating["type_ar"], (10, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        cv2.imshow("Head Pose Test", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
    
# -------------------------
# الكود الصحيح لطالب واحد فقط
# import cv2 #تشغيل الكاميرا ومعالجة الصور والفيديو
# import time #حساب الزمن ومدة استمرار السلوك
# import insightface #مكتبه تتبع حركه الراس
# from collections import defaultdict #تخزين أوقات الحالات دون ظهور أخطاء عند عدم وجود مفتاح
# #
# import winsound  # الصوت على Windows


# class HeadPoseService:

#     def __init__(self):

#         # 🔹 تحميل موديل الوجه
#         self.app = insightface.app.FaceAnalysis(name="buffalo_l")
#         self.app.prepare(ctx_id=-1, det_size=(320, 320))  # حجم أصغر للكشف الأسرع

#         # 🔹 حدود الحركة
#         self.yaw_threshold = 30   #  التفت يمين/يسار 30 درجه واستمر في الاتفات لمده 0.3 حاله غش
#         self.pitch_threshold = 25 # حركة رأس للأعلى/الأسفل 25 درجه واستمر 0.5

#         # ⏱️ الوقت بالثواني لتحديد الغش
#         self.required_seconds = {
#             "look_away": 0.5,
#             "head_movement": 0.3,
#             "no_face": 3  # وجه مختفي أكثر من 2 ثواني = غش
#         }

#         # ⏱️ وقت بدء الحالة
#         #وهذا هي مهمه مكتبه التي تمنع الاخطا نفترض انه لايوجد داخل القاموس  لن يتوقف النظام بل سيطبع كلمه نن none 
#         #"look_away": 0.5,
#         # "head_movement": 0.3,
#         # "no_face": 3 
#         self.start_time = defaultdict(lambda: None)

#         # ⛔ منع التكرار
#         self.cooldown = 5  # ثواني
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
#             # تصغير الفريم لتسريع المعالجة
#             height, width = frame.shape[:2]
#             if width > 640:
#                 scale = 640 / width
#                 new_width = 640
#                 new_height = int(height * scale)
#                 frame_small = cv2.resize(frame, (new_width, new_height))
#             else:
#                 frame_small = frame
                
#             faces = self.app.get(frame_small)
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
#                             "cheating_type_id": 4,
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
# ----------------------------------
#  لاخر تحديث حاليا الصح
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



