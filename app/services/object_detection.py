# import cv2
# from ultralytics import YOLO


# class ObjectDetectionService:

#     def __init__(self):
#         self.model = YOLO("yolov8n.pt")
#         self.confidence_threshold = 0.6
          # يمكنك تعديل هذه القيمة

        # الأشياء التي نعتبرها غش (العربي + الإنجليزي)
    #     self.cheating_objects = {
    #         "cell phone": {"ar": "استخدام الهاتف", "en": "Using Phone"},
    #         "earphone": {"ar": "استخدام سماعات", "en": "Using Earphones"},
    #         "headphones": {"ar": "استخدام سماعات", "en": "Using Headphones"}
    #     }

    # def detect_objects(self, frame):
    #     results = self.model(frame, verbose=False)
    #     detections = []
    #     person_count = 0

    #     for result in results:
    #         for box in result.boxes:
    #             class_id = int(box.cls[0])
    #             confidence = float(box.conf[0])
    #             label = self.model.names[class_id]

    #             # عد الأشخاص فقط إذا كانت الثقة أعلى من العتبة
    #             if label == "person" and confidence > self.confidence_threshold:
    #                 person_count += 1

    #             # اكتشاف أجسام الغش الأخرى (هاتف، سماعات) بشرط الثقة
    #             if label in self.cheating_objects and confidence > self.confidence_threshold:
    #                 detections.append({
    #                     "label": label,
    #                     "confidence": confidence,
    #                     "ar": self.cheating_objects[label]["ar"],
    #                     "en": self.cheating_objects[label]["en"]
    #                 })

    #     return detections, person_count

    # def detect_cheating(self, frame):
    #     detections, person_count = self.detect_objects(frame)
    #     cheating_events = []

        # إضافة الغش الآخر (الهاتف، السماعات...)
        # for d in detections:
        #     cheating_events.append({
        #         "type_ar": d["ar"],
        #         "type_en": d["en"],
        #         "confidence": d["confidence"]
        #     })

        # # إذا كان هناك أكثر من شخص (بعد تطبيق شرط الثقة)
        # if person_count > 1:
        #     cheating_events.append({
        #         "type_ar": "وجود شخص آخر",
        #         "type_en": "Another Person Detected",
        #         "confidence": 1.0
        #     })

        # return cheating_events


# مثال تشغيل للاختبار فقط
# if __name__ == "__main__":
#     detector = ObjectDetectionService()
#     cap = cv2.VideoCapture(0)

#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             break

#         cheating = detector.detect_cheating(frame)

        # طباعة أحداث الغش إن وجدت
    #     if cheating:
    #         for c in cheating:
    #             print(f"{c['type_ar']} | {c['type_en']} - Confidence: {c['confidence']:.2f}")

    #     cv2.imshow("Camera", frame)

    #     if cv2.waitKey(1) & 0xFF == 27:  # ESC للخروج
    #         break

    # cap.release()
    # cv2.destroyAllWindows()
    # ---------------------------------------
# import cv2
# from ultralytics import YOLOWorld  # 👈 استيراد مختلف

# class ObjectDetectionService:
#     def __init__(self):
#         # تحميل نموذج YOLO-World (أصغر وأسرع نموذج)
#         self.model = YOLOWorld("yolov8s-worldv2.pt")  # أو استخدم yolov8m-world.pt للأداء الأفضل
#         self.confidence_threshold = 0.3  # ثقة أقل لأن السماعات صغيرة
        
#         # تحديد الكلمات التي نريد اكتشافها
#         self.model.set_classes(["headphones", "earphone", "earbuds", "cell phone"])
        
#         # الأشياء التي نعتبرها غش
#         self.cheating_objects = {
#             "headphones": {"ar": "استخدام سماعات", "en": "Using Headphones"},
#             "earphone": {"ar": "استخدام سماعات", "en": "Using Earphones"},
#             "earbuds": {"ar": "استخدام سماعات", "en": "Using Earbuds"},
#             "cell phone": {"ar": "استخدام الهاتف", "en": "Using Phone"}
#         }

#     def detect_objects(self, frame):
#         results = self.model(frame, verbose=False)
#         detections = []
#         person_count = 0

#         for result in results:
#             for box in result.boxes:
#                 class_id = int(box.cls[0])
#                 confidence = float(box.conf[0])
#                 label = self.model.names[class_id]  # الآن ستحصل على "headphones" وليس رقم

#                 # عد الأشخاص (YOLO-World لايزال يتعرف على person)
#                 if label == "person" and confidence > self.confidence_threshold:
#                     person_count += 1

#                 # اكتشاف أجسام الغش
#                 if label in self.cheating_objects and confidence > self.confidence_threshold:
#                     detections.append({
#                         "label": label,
#                         "confidence": confidence,
#                         "ar": self.cheating_objects[label]["ar"],
#                         "en": self.cheating_objects[label]["en"]
#                     })

#         return detections, person_count

#     # باقي الدوال كما هي...
#     def detect_cheating(self, frame):
#         detections, person_count = self.detect_objects(frame)
#         cheating_events = []

#         for d in detections:
#             cheating_events.append({
#                 "type_ar": d["ar"],
#                 "type_en": d["en"],
#                 "confidence": d["confidence"]
#             })

#         if person_count > 1:
#             cheating_events.append({
#                 "type_ar": "وجود شخص آخر",
#                 "type_en": "Another Person Detected",
#                 "confidence": 1.0
#             })

#         return cheating_events

# # نفس طريقة التشغيل السابقة
# if __name__ == "__main__":
#     detector = ObjectDetectionService()
#     cap = cv2.VideoCapture(0)

#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             break

#         cheating = detector.detect_cheating(frame)

#         if cheating:
#             for c in cheating:
#                 print(f"{c['type_ar']} | {c['type_en']} - Confidence: {c['confidence']:.2f}")

#         cv2.imshow("Camera", frame)
#         if cv2.waitKey(1) & 0xFF == 27:
#             break

#     cap.release()
#     cv2.destroyAllWindows()
# app/services/object_detection.py

# class ObjectDetectionService:
#     def __init__(self):
#         pass

#     def detect_objects(self, frame):
#         # مؤقتاً، لا شيء يرجع دائماً قائمة فارغة وعدد أشخاص صفر
#         return [], 0

#     def detect_cheating(self, frame):
#         # مؤقتاً، لا يوجد أي غش
#         return []
# ------------------------------------
# import cv2
# from ultralytics import YOLOWorld


# class ObjectDetectionService:
#     def __init__(self):
#         print("⏳ Loading YOLO-World model...")
#         self.model = YOLOWorld("yolov8s-worldv2.pt")

#         # threshold منخفض للسماعات الصغيرة
#         self.confidence_threshold = 0.25

#         # كل التسميات الممكنة للسماعات — YOLO-World يفهم النص
#         self.earphone_aliases = [
#             "earphone",
#             "earphones",
#             "earbuds",
#             "earbud",
#             "headphones",
#             "headphone",
#             "wireless earbuds",
#             "in-ear headphones",
#             "airpods",
#             "hearing device",
#         ]

#         # الكلاسات الكاملة
#         all_classes = self.earphone_aliases + ["cell phone", "person", "mobile phone", "smartphone"]
#         self.model.set_classes(all_classes)

#         # تعريف الغش — أي تسمية سماعة تُعامل كغش
#         self.cheating_map = {alias: "استخدام سماعات" for alias in self.earphone_aliases}
#         self.cheating_map["cell phone"] = "استخدام الهاتف"
#         self.cheating_map["mobile phone"] = "استخدام الهاتف"
#         self.cheating_map["smartphone"] = "استخدام الهاتف"

#         # cheating_type_id لكل نوع
#         self.cheating_type_ids = {
#             "استخدام سماعات": 2,
#             "استخدام الهاتف": 1,
#             "وجود أكثر من شخص": 3,
#         }

#         # منع تكرار نفس الكشف خلال ثواني
#         self.last_detected = {}
#         self.detection_cooldown = 3  # ثواني

#         print("✅ Model loaded successfully")

#     # =========================
#     # الكشف الرئيسي
#     # =========================
#     def detect(self, frame):
#         results = self.model(frame, verbose=False)
#         detections = []
#         person_count = 0

#         for result in results:
#             for box in result.boxes:
#                 class_id = int(box.cls[0])
#                 confidence = float(box.conf[0])
#                 label = self.model.names[class_id].lower()

#                 # threshold مخصص للسماعات أقل من الهاتف
#                 threshold = 0.20 if label in self.earphone_aliases else self.confidence_threshold
#                 if confidence < threshold:
#                     continue

#                 x1, y1, x2, y2 = map(int, box.xyxy[0])

#                 if label == "person":
#                     person_count += 1
#                     cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
#                     cv2.putText(frame, f"person {confidence:.2f}",
#                                 (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
#                     continue

#                 if label in self.cheating_map:
#                     cheating_type = self.cheating_map[label]
#                     # رسم المستطيل
#                     color = (0, 0, 255) if "هاتف" in cheating_type else (255, 0, 0)
#                     cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
#                     cv2.putText(frame, f"{label} {confidence:.2f}",
#                                 (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

#                     detections.append({
#                         "label": label,
#                         "confidence": confidence,
#                         "type_ar": cheating_type,
#                         "cheating_type_id": self.cheating_type_ids.get(cheating_type, 0),
#                         "bbox": (x1, y1, x2, y2),
#                     })

#         # كشف أكثر من شخص
#         if person_count > 1:
#             detections.append({
#                 "label": "multiple_persons",
#                 "confidence": 1.0,
#                 "type_ar": "وجود أكثر من شخص",
#                 "cheating_type_id": self.cheating_type_ids["وجود أكثر من شخص"],
#                 "bbox": None,
#             })

#         return frame, detections, person_count

#     # =========================
#     # للاستخدام من VideoMonitoringService
#     # =========================
#     def detect_cheating(self, frame):
#         frame, detections, person_count = self.detect(frame)
#         return detections

#     # =========================
#     # تشغيل مستقل للاختبار
#     # =========================


# if __name__ == "__main__":
#     import time

#     detector = ObjectDetectionService()
#     cap = cv2.VideoCapture(0)

#     if not cap.isOpened():
#         print("❌ Cannot open camera")
#         exit()

#     print("🎥 Camera started... Press ESC to exit")
#     last_print = 0

#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             break

#         frame, detections, person_count = detector.detect(frame)

#         now = time.time()
#         if detections and now - last_print > 1:
#             print("\n🚨 Cheating Detected:")
#             for d in detections:
#                 print(f"  {d['type_ar']} | {d['label']} | confidence: {d['confidence']:.2f}")
#             last_print = now

#         if person_count > 1:
#             cv2.putText(frame, "⚠ Multiple Persons!", (20, 120),
#                         cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

#         cv2.imshow("Detection Test", frame)
#         if cv2.waitKey(1) & 0xFF == 27:
#             break

#     cap.release()
#     cv2.destroyAllWindows()
# ------------------------------------
# import cv2
# import time
# from collections import defaultdict
# from ultralytics import YOLOWorld


# class ObjectDetectionService:
#     def __init__(self):
#         print("⏳ Loading YOLO-World model...")
#         self.model = YOLOWorld("yolov8s-worldv2.pt")

#         self.earphone_aliases = [
#             "earphone", "earphones", "earbuds", "earbud",
#             "headphones", "headphone", "wireless earbuds",
#             "in-ear headphones", "airpods",
#         ]

#         all_classes = self.earphone_aliases + ["cell phone", "person", "mobile phone", "smartphone"]
#         self.model.set_classes(all_classes)

#         self.cheating_map = {alias: "استخدام سماعات" for alias in self.earphone_aliases}
#         self.cheating_map["cell phone"]   = "استخدام الهاتف"
#         self.cheating_map["mobile phone"] = "استخدام الهاتف"
#         self.cheating_map["smartphone"]   = "استخدام الهاتف"

#         self.cheating_type_ids = {
#             "استخدام سماعات":    2,
#             "استخدام الهاتف":    1,
#             "وجود أكثر من شخص": 3,
#         }

#         # threshold أعلى لتقليل false positives
#         self.phone_threshold    = 0.55   # هاتف — يحتاج ثقة عالية
#         self.earphone_threshold = 0.30   # سماعات — أصغر حجماً

#         # نظام التأكيد: كم فريم متتالي قبل الإعلان
#         self.confirm_frames_needed = {
#             "استخدام الهاتف":    3,   # 3 فريمات متتالية
#             "استخدام سماعات":    2,   # 2 فريم متتالي
#             "وجود أكثر من شخص": 4,
#         }
#         # عداد الفريمات المتتالية لكل نوع
#         self.consecutive_count = defaultdict(int)

#         # cooldown بعد الإعلان (ثواني)
#         self.cooldown = 8
#         self.last_reported = {}

#         print("✅ Model loaded successfully")

#     # =========================
#     # الكشف الرئيسي
#     # =========================
#     def detect(self, frame):
#         results = self.model(frame, verbose=False)

#         found_types = set()   # ما وجده النموذج في هذا الفريم
#         person_count = 0

#         for result in results:
#             for box in result.boxes:
#                 class_id   = int(box.cls[0])
#                 confidence = float(box.conf[0])
#                 label      = self.model.names[class_id].lower()

#                 if label == "person":
#                     person_count += 1
#                     x1, y1, x2, y2 = map(int, box.xyxy[0])
#                     cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
#                     continue

#                 if label in self.cheating_map:
#                     cheating_type = self.cheating_map[label]
#                     threshold = (self.phone_threshold
#                                  if "هاتف" in cheating_type
#                                  else self.earphone_threshold)

#                     if confidence < threshold:
#                         continue

#                     x1, y1, x2, y2 = map(int, box.xyxy[0])
#                     color = (0, 0, 255) if "هاتف" in cheating_type else (255, 0, 0)
#                     cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
#                     cv2.putText(frame, f"{label} {confidence:.2f}",
#                                 (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

#                     found_types.add((cheating_type, label, confidence))

#         if person_count > 1:
#             found_types.add(("وجود أكثر من شخص", "multiple_persons", 1.0))

#         # تحديث عدادات التأكيد
#         confirmed_detections = []
#         all_cheating_types = set(ct for ct, _, _ in found_types)

#         for cheating_type, label, confidence in found_types:
#             self.consecutive_count[cheating_type] += 1
#             needed = self.confirm_frames_needed.get(cheating_type, 3)

#             if self.consecutive_count[cheating_type] >= needed:
#                 now = time.time()
#                 last = self.last_reported.get(cheating_type, 0)
#                 if now - last >= self.cooldown:
#                     self.last_reported[cheating_type] = now
#                     confirmed_detections.append({
#                         "label":           label,
#                         "confidence":      confidence,
#                         "type_ar":         cheating_type,
#                         "cheating_type_id": self.cheating_type_ids.get(cheating_type, 0),
#                     })

#         # إعادة تصفير العدادات لما لم يُكتشف في هذا الفريم
#         for cheating_type in list(self.consecutive_count.keys()):
#             if cheating_type not in all_cheating_types:
#                 self.consecutive_count[cheating_type] = 0

#         return frame, confirmed_detections, person_count

#     # =========================
#     # للاستخدام من VideoMonitoringService
#     # =========================
#     def detect_cheating(self, frame):
#         frame, detections, _ = self.detect(frame)
#         return detections


# # =========================
# # تشغيل مستقل للاختبار
# # =========================
# if __name__ == "__main__":
#     detector = ObjectDetectionService()
#     cap = cv2.VideoCapture(0)

#     if not cap.isOpened():
#         print("❌ Cannot open camera")
#         exit()

#     print("🎥 Camera started... Press ESC to exit")

#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             break

#         frame, detections, person_count = detector.detect(frame)

#         for d in detections:
#             print(f"🚨 {d['type_ar']} | {d['label']} | {d['confidence']:.2f}")

#         cv2.imshow("Detection Test", frame)
#         if cv2.waitKey(1) & 0xFF == 27:
#             break

#     cap.release()
#     cv2.destroyAllWindows()

# -------------------------------------------
import cv2
import time
from collections import defaultdict
from ultralytics import YOLOWorld


class ObjectDetectionService:
    def __init__(self):
        print("⏳ Loading YOLO-World model...")
        self.model = YOLOWorld("yolov8s-worldv2.pt")

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
            "استخدام الهاتف": 1,
            "استخدام سماعات": 2,
            "وجود شخص آخر": 3,
        }

        self.phone_threshold = 0.55
        self.earphone_threshold = 0.30

        self.confirm_frames_needed = {
            "استخدام الهاتف": 3,
            "استخدام سماعات": 2,
            "وجود شخص آخر": 4,
        }

        self.consecutive_count = defaultdict(int)

        self.cooldown = 8
        self.last_reported = {}

        print("✅ Model loaded successfully")

    # =========================
    # الكشف الأساسي
    # =========================
    def detect(self, frame):
        results = self.model(frame, verbose=False)

        found_types = set()
        person_count = 0

        for result in results:
            for box in result.boxes:
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                label = self.model.names[class_id].lower()

                # عد الأشخاص
                if label == "person":
                    person_count += 1
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

        # أكثر من شخص
        if person_count > 1:
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

                if now - last >= self.cooldown:
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
    