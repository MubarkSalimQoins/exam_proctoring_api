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

class ObjectDetectionService:
    def __init__(self):
        pass

    def detect_objects(self, frame):
        # مؤقتاً، لا شيء يرجع دائماً قائمة فارغة وعدد أشخاص صفر
        return [], 0

    def detect_cheating(self, frame):
        # مؤقتاً، لا يوجد أي غش
        return []