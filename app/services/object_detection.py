import cv2
import time
import numpy as np
from collections import defaultdict
from ultralytics import YOLOWorld
import insightface


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
            "استخدام الهاتف": 1,
            "استخدام سماعات": 3,
        }

        self.phone_threshold = 0.15
        self.earphone_threshold = 0.20

        # كشف فوري - فريم واحد فقط
        self.confirm_frames_needed = {
            "استخدام الهاتف": 1,
            "استخدام سماعات": 1,
        }

        self.consecutive_count = defaultdict(int)

        self.cooldown = 5
        self.phone_cooldown = 2
        self.person_cooldown = 2
        self.last_reported = {}

        # ✅ تحميل موديل التعرف على الوجه
        print("⏳ Loading Face model for object detection...")
        self.face_app = insightface.app.FaceAnalysis(name="buffalo_l")
        self.face_app.prepare(ctx_id=-1, det_size=(320, 320))
        print("✅ Face model loaded")

        print("✅ Model loaded successfully")

    # =========================
    # ✅ دالة مساعدة: استخراج الوجوه مع مواقعها
    # =========================
    def _get_faces_with_positions(self, frame):
        """استخراج الوجوه مع مواقعها في الفريم"""
        try:
            faces = self.face_app.get(frame)
            result = []
            for f in faces:
                x1, y1, x2, y2 = f.bbox
                center_x = (x1 + x2) / 2
                center_y = (y1 + y2) / 2
                result.append({
                    "embedding": f.embedding.astype(np.float32).tobytes(),
                    "center_x": center_x,
                    "center_y": center_y,
                    "bbox": (x1, y1, x2, y2)
                })
            return result
        except Exception as e:
            print(f"⚠️ خطأ في استخراج الوجوه: {e}")
            return []

    # =========================
    # ✅ دالة مساعدة: إيجاد أقرب وجه لموقع الهاتف/السماعة
    # =========================
    def _get_nearest_face_embedding(self, faces, object_box):
        """يرجع embedding الوجه الأقرب مكانياً للكائن (هاتف/سماعة)"""
        if not faces:
            return None

        ox1, oy1, ox2, oy2 = object_box
        obj_cx = (ox1 + ox2) / 2
        obj_cy = (oy1 + oy2) / 2

        best_face = None
        best_dist = float("inf")

        for face in faces:
            dist = ((face["center_x"] - obj_cx) ** 2 + (face["center_y"] - obj_cy) ** 2) ** 0.5
            if dist < best_dist:
                best_dist = dist
                best_face = face

        if best_face:
            print(f"🎯 أقرب وجه للكائن: مسافة {best_dist:.1f}px")
            return best_face["embedding"]

        return None

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

        # cheating_type -> (label, confidence, box)
        found_types = {}
        person_detections = []

        for result in results:
            for box in result.boxes:
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                label = self.model.names[class_id].lower()

                if label == "person":
                    if confidence > 0.5:
                        x1, y1, x2, y2 = box.xyxy[0].tolist()
                        area = (x2 - x1) * (y2 - y1)
                        person_detections.append({
                            'confidence': confidence,
                            'area': area,
                            'box': (x1, y1, x2, y2)
                        })
                    continue

                if label in self.cheating_map:
                    cheating_type = self.cheating_map[label]

                    threshold = (
                        self.phone_threshold
                        if "هاتف" in cheating_type
                        else self.earphone_threshold
                    )

                    if confidence < threshold:
                        continue

                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    # احتفظ بأعلى confidence لكل نوع مع موقعه
                    if cheating_type not in found_types or confidence > found_types[cheating_type][1]:
                        found_types[cheating_type] = (label, confidence, (x1, y1, x2, y2))

        # فلترة الأشخاص
        if len(person_detections) > 1:
            person_detections.sort(key=lambda x: x['area'], reverse=True)
            main_person = person_detections[0]
            real_persons = 1
            for person in person_detections[1:]:
                if person['area'] > main_person['area'] * 0.3 and person['confidence'] > 0.65:
                    real_persons += 1

        # نظام التأكيد + cooldown
        confirmed_detections = []
        all_cheating_types = set(found_types.keys())

        # ✅ استخراج الوجوه مع مواقعها مرة واحدة فقط
        faces_with_positions = self._get_faces_with_positions(frame_resized)

        for cheating_type, (label, confidence, obj_box) in found_types.items():
            self.consecutive_count[cheating_type] += 1
            needed = self.confirm_frames_needed.get(cheating_type, 3)

            if self.consecutive_count[cheating_type] >= needed:
                now = time.time()
                last = self.last_reported.get(cheating_type, 0)

                if "هاتف" in cheating_type:
                    cooldown_time = self.phone_cooldown
                elif "شخص" in cheating_type:
                    cooldown_time = self.person_cooldown
                else:
                    cooldown_time = self.cooldown

                if now - last >= cooldown_time:
                    self.last_reported[cheating_type] = now

                    detection = {
                        "label": label,
                        "confidence": confidence,
                        "type_ar": cheating_type,
                        "cheating_type_id": self.cheating_type_ids.get(cheating_type, 0),
                    }

                    # ✅ أقرب وجه لموقع الكائن
                    nearest_emb = self._get_nearest_face_embedding(faces_with_positions, obj_box)
                    if nearest_emb:
                        detection["face_embedding"] = nearest_emb

                    confirmed_detections.append(detection)

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
    # كشف الهاتف فقط - سريع جداً
    # =========================
    def detect_phone_only(self, frame):
        """كشف الهاتف بشكل منفصل وأسرع"""
        height, width = frame.shape[:2]
        if width > 640:
            scale = 640 / width
            frame_resized = cv2.resize(frame, (640, int(height * scale)))
        else:
            frame_resized = frame

        results = self.model(frame_resized, verbose=False, imgsz=640)

        phone_labels = ["cell phone", "mobile phone", "smartphone"]

        for result in results:
            for box in result.boxes:
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                label = self.model.names[class_id].lower()

                if label in phone_labels and confidence > 0.15:
                    now = time.time()
                    last = self.last_reported.get("استخدام الهاتف", 0)

                    if now - last >= self.phone_cooldown:
                        self.last_reported["استخدام الهاتف"] = now

                        # ✅ موقع الهاتف
                        x1, y1, x2, y2 = box.xyxy[0].tolist()
                        phone_box = (x1, y1, x2, y2)

                        # ✅ أقرب وجه لموقع الهاتف = الطالب الذي يمسكه
                        faces = self._get_faces_with_positions(frame_resized)
                        nearest_emb = self._get_nearest_face_embedding(faces, phone_box)

                        detection = {
                            "label": label,
                            "confidence": confidence,
                            "type_ar": "استخدام الهاتف",
                            "cheating_type_id": self.cheating_type_ids.get("استخدام الهاتف", 0),
                        }

                        if nearest_emb:
                            detection["face_embedding"] = nearest_emb

                        return [detection]

        return []

    # =========================
    # كشف الأشياء الأخرى (سماعات + شخص)
    # =========================
    def detect_other_cheating(self, frame):
        """كشف السماعات والشخص بشكل منفصل"""
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
# -------
# هذا حق الهاتف وجود شخص اخر 
# import cv2
# import time
# from collections import defaultdict
# from ultralytics import YOLOWorld


# class ObjectDetectionService:
#     def __init__(self):
#         print("⏳ Loading YOLO-World model...")
#         self.model = YOLOWorld("yolov8s-worldv2.pt")
        
#         # تحسينات الأداء
#         self.model.overrides['conf'] = 0.25  # threshold أعلى
#         self.model.overrides['iou'] = 0.45
#         self.model.overrides['half'] = False  # FP16 للسرعة (إذا كان GPU متاح)

#         self.earphone_aliases = [
#             "earphone", "earphones", "earbuds", "earbud",
#             "headphones", "headphone", "wireless earbuds",
#             "in-ear headphones", "airpods",
#         ]

#         all_classes = self.earphone_aliases + [
#             "cell phone", "person", "mobile phone", "smartphone"
#         ]
#         self.model.set_classes(all_classes)

#         self.cheating_map = {alias: "استخدام سماعات" for alias in self.earphone_aliases}
#         self.cheating_map["cell phone"] = "استخدام الهاتف"
#         self.cheating_map["mobile phone"] = "استخدام الهاتف"
#         self.cheating_map["smartphone"] = "استخدام الهاتف"

#         self.cheating_type_ids = {
#             "استخدام الهاتف": 1,#4
#             "استخدام سماعات": 3,#3
#             "وجود شخص آخر": 2,#2
#         }
        

#         self.phone_threshold = 0.15  #很低 للكشف حتى الجزء الصغير
#         self.earphone_threshold = 0.20  # أقل للسماعات أيضاً

#         # كشف فوري - فريم واحد فقط
#         self.confirm_frames_needed = {
#             "استخدام الهاتف": 1,  # فوري - فريم واحد فقط!
#             "استخدام سماعات": 1,  # فوري أيضاً
#             "وجود شخص آخر": 1,  # فوري للشخص الثاني
#         }

#         self.consecutive_count = defaultdict(int)

#         self.cooldown = 5  # cooldown عام
#         self.phone_cooldown = 2  # cooldown للهاتف - سريع
#         self.person_cooldown = 1  # cooldown للشخص الثاني - سريع
#         self.last_reported = {}

#         print("✅ Model loaded successfully")

#     # =========================
#     # الكشف الأساسي
#     # =========================
#     def detect(self, frame):
#         # تصغير الفريم لتسريع المعالجة
#         height, width = frame.shape[:2]
#         if width > 640:
#             scale = 640 / width
#             new_width = 640
#             new_height = int(height * scale)
#             frame_resized = cv2.resize(frame, (new_width, new_height))
#         else:
#             frame_resized = frame
            
#         results = self.model(frame_resized, verbose=False, imgsz=640)

#         found_types = set()
#         person_detections = []

#         for result in results:
#             for box in result.boxes:
#                 class_id = int(box.cls[0])
#                 confidence = float(box.conf[0])
#                 label = self.model.names[class_id].lower()

#                 # جمع معلومات الأشخاص
#                 if label == "person":
#                     # فقط الأشخاص بثقة عالية
#                     if confidence > 0.5:
#                         x1, y1, x2, y2 = box.xyxy[0].tolist()
#                         area = (x2 - x1) * (y2 - y1)
#                         person_detections.append({
#                             'confidence': confidence,
#                             'area': area,
#                             'box': (x1, y1, x2, y2)
#                         })
#                     continue

#                 # كشف الغش
#                 if label in self.cheating_map:
#                     cheating_type = self.cheating_map[label]

#                     threshold = (
#                         self.phone_threshold
#                         if "هاتف" in cheating_type
#                         else self.earphone_threshold
#                     )

#                     if confidence < threshold:
#                         continue

#                     found_types.add((cheating_type, label, confidence))

#         # فلترة الأشخاص - إزالة الكشوفات الصغيرة والضعيفة
#         if len(person_detections) > 1:
#             # ترتيب حسب المساحة (الأكبر أولاً)
#             person_detections.sort(key=lambda x: x['area'], reverse=True)
            
#             # الشخص الرئيسي (الأكبر)
#             main_person = person_detections[0]
            
#             # فحص الأشخاص الآخرين
#             real_persons = 1
#             for person in person_detections[1:]:
#                 # إذا كان الشخص الآخر كبير بما يكفي (أكثر من 30% من الرئيسي)
#                 # وثقة عالية (أكثر من 0.65)
#                 if person['area'] > main_person['area'] * 0.3 and person['confidence'] > 0.65:
#                     real_persons += 1
            
#             # فقط إذا كان هناك شخصان حقيقيان
#             if real_persons > 1:
#                 found_types.add(("وجود شخص آخر", "multiple_persons", 1.0))

#         # =========================
#         # نظام التأكيد + cooldown
#         # =========================
#         confirmed_detections = []
#         all_cheating_types = set(ct for ct, _, _ in found_types)

#         for cheating_type, label, confidence in found_types:
#             self.consecutive_count[cheating_type] += 1
#             needed = self.confirm_frames_needed.get(cheating_type, 3)

#             if self.consecutive_count[cheating_type] >= needed:
#                 now = time.time()
#                 last = self.last_reported.get(cheating_type, 0)
                
#                 # استخدام cooldown مختلف حسب النوع
#                 if "هاتف" in cheating_type:
#                     cooldown_time = self.phone_cooldown
#                 elif "شخص" in cheating_type:
#                     cooldown_time = self.person_cooldown
#                 else:
#                     cooldown_time = self.cooldown

#                 if now - last >= cooldown_time:
#                     self.last_reported[cheating_type] = now

#                     confirmed_detections.append({
#                         "label": label,
#                         "confidence": confidence,
#                         "type_ar": cheating_type,
#                         "cheating_type_id": self.cheating_type_ids.get(cheating_type, 0),
#                     })

#         # إعادة التصفير
#         for cheating_type in list(self.consecutive_count.keys()):
#             if cheating_type not in all_cheating_types:
#                 self.consecutive_count[cheating_type] = 0

#         return confirmed_detections

#     # =========================
#     # هذه هي المهمة (مطلوبة من video_service)
#     # =========================
#     def detect_cheating(self, frame):
#         return self.detect(frame)

#     # =========================
#     # كشف الهاتف فقط - سريع جداً
#     # =========================
#     def detect_phone_only(self, frame):
#         """كشف الهاتف بشكل منفصل وأسرع"""
#         # تصغير الفريم
#         height, width = frame.shape[:2]
#         if width > 640:
#             scale = 640 / width
#             frame_resized = cv2.resize(frame, (640, int(height * scale)))
#         else:
#             frame_resized = frame
            
#         results = self.model(frame_resized, verbose=False, imgsz=640)
        
#         phone_labels = ["cell phone", "mobile phone", "smartphone"]
        
#         for result in results:
#             for box in result.boxes:
#                 class_id = int(box.cls[0])
#                 confidence = float(box.conf[0])
#                 label = self.model.names[class_id].lower()
                
#                 if label in phone_labels and confidence > 0.15:  #很低 threshold
#                     # فحص cooldown
#                     now = time.time()
#                     last = self.last_reported.get("استخدام الهاتف", 0)
                    
#                     if now - last >= self.phone_cooldown:
#                         self.last_reported["استخدام الهاتف"] = now
#                         return [{
#                             "label": label,
#                             "confidence": confidence,
#                             "type_ar": "استخدام الهاتف",
#                             "cheating_type_id": self.cheating_type_ids.get("استخدام الهاتف", 0),
#                         }]
        
#         return []

#     # =========================
#     # كشف الأشياء الأخرى (سماعات + شخص)
#     # =========================
#     def detect_other_cheating(self, frame):
#         """كشف السماعات والشخص بشكل منفصل"""
#         return self.detect(frame)


# # =========================
# # تشغيل للاختبار فقط
# # =========================
# if __name__ == "__main__":
#     detector = ObjectDetectionService()
#     cap = cv2.VideoCapture(0)

#     print("🎥 Camera started...")

#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             break

#         detections = detector.detect_cheating(frame)

#         for d in detections:
#             print(f"🚨 {d['type_ar']} | {d['label']} | {d['confidence']:.2f}")

#         cv2.imshow("Test", frame)

#         if cv2.waitKey(1) & 0xFF == 27:
#             break

#     cap.release()
#     cv2.destroyAllWindows()
    
        
    
# ------------------------------------------- كود كاميرا الجهاز
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

#         all_classes = self.earphone_aliases + [
#             "cell phone", "person", "mobile phone", "smartphone"
#         ]
#         self.model.set_classes(all_classes)

#         self.cheating_map = {alias: "استخدام سماعات" for alias in self.earphone_aliases}
#         self.cheating_map["cell phone"] = "استخدام الهاتف"
#         self.cheating_map["mobile phone"] = "استخدام الهاتف"
#         self.cheating_map["smartphone"] = "استخدام الهاتف"

#         self.cheating_type_ids = {
#             "استخدام الهاتف": 1,#4
#             "استخدام سماعات": 3,#3
#             "وجود شخص آخر": 2,#2
#         }
        

#         self.phone_threshold = 0.35
#         self.earphone_threshold = 0.30

#         self.confirm_frames_needed = {
#             "استخدام الهاتف": 1,#4
#             "استخدام سماعات": 2,#3
#             "وجود شخص آخر": 4,#4
#         }

#         self.consecutive_count = defaultdict(int)

#         self.cooldown = 8
#         self.last_reported = {}

#         print("✅ Model loaded successfully")

#     # =========================
#     # الكشف الأساسي
#     # =========================
#     def detect(self, frame):
#         results = self.model(frame, verbose=False)

#         found_types = set()
#         person_count = 0

#         for result in results:
#             for box in result.boxes:
#                 class_id = int(box.cls[0])
#                 confidence = float(box.conf[0])
#                 label = self.model.names[class_id].lower()

#                 # عد الأشخاص
#                 if label == "person":
#                     person_count += 1
#                     continue

#                 # كشف الغش
#                 if label in self.cheating_map:
#                     cheating_type = self.cheating_map[label]

#                     threshold = (
#                         self.phone_threshold
#                         if "هاتف" in cheating_type
#                         else self.earphone_threshold
#                     )

#                     if confidence < threshold:
#                         continue

#                     found_types.add((cheating_type, label, confidence))

#         # أكثر من شخص
#         if person_count > 1:
#             found_types.add(("وجود شخص آخر", "multiple_persons", 1.0))

#         # =========================
#         # نظام التأكيد + cooldown
#         # =========================
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
#                         "label": label,
#                         "confidence": confidence,
#                         "type_ar": cheating_type,
#                         "cheating_type_id": self.cheating_type_ids.get(cheating_type, 0),
#                     })

#         # إعادة التصفير
#         for cheating_type in list(self.consecutive_count.keys()):
#             if cheating_type not in all_cheating_types:
#                 self.consecutive_count[cheating_type] = 0

#         return confirmed_detections

#     # =========================
#     # هذه هي المهمة (مطلوبة من video_service)
#     # =========================
#     def detect_cheating(self, frame):
#         return self.detect(frame)


# # =========================
# # تشغيل للاختبار فقط
# # =========================
# if __name__ == "__main__":
#     detector = ObjectDetectionService()
#     cap = cv2.VideoCapture(0)

#     print("🎥 Camera started...")

#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             break

#         detections = detector.detect_cheating(frame)

#         for d in detections:
#             print(f"🚨 {d['type_ar']} | {d['label']} | {d['confidence']:.2f}")

#         cv2.imshow("Test", frame)

#         if cv2.waitKey(1) & 0xFF == 27:
#             break

#     cap.release()
#     cv2.destroyAllWindows()
    