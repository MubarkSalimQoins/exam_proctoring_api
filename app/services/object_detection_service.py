import cv2
from ultralytics import YOLO


class ObjectDetectionService:

    def _init_(self):
        # تحميل موديل YOLO
        self.model = YOLO("yolov8n.pt")

        # الأشياء التي نعتبرها غش
        self.cheating_objects = {
            "cell phone": "استخدام الهاتف",
            "person": "وجود شخص آخر",
            "earphone": "استخدام سماعات",
            "headphones": "استخدام سماعات"
        }

    def detect_objects(self, frame):
        """
        تحليل Frame من الكاميرا واكتشاف الأشياء
        """

    #    تحليل الصورة القادمه من الكيمرا
        results = self.model(frame, verbose=False)

        detections = []

        for result in results:
            for box in result.boxes:

                class_id = int(box.cls[0])
                confidence = float(box.conf[0])

                label = self.model.names[class_id]

                if label in self.cheating_objects:

                    detections.append({
                        "label": label,
                        "cheating_type": self.cheating_objects[label],
                        "confidence": confidence
                    })

        return detections

    def detect_cheating(self, frame):
        """
        تحديد إذا كان هناك غش في الصورة
        """

        detections = self.detect_objects(frame)

        cheating_events = []

        person_count = 0

        for d in detections:

            if d["label"] == "person":
                person_count += 1

            cheating_events.append({
                "type": d["cheating_type"],
                "confidence": d["confidence"]
            })

        # إذا كان هناك أكثر من شخص
        if person_count > 1:
            cheating_events.append({
                "type": "وجود شخص آخر",
                "confidence": 1.0
            })

        return cheating_events


# مثال تشغيل للاختبار فقط
if _name_ == "_main_":

    detector = ObjectDetectionService()

    cap = cv2.VideoCapture(0)

    while True:

        ret, frame = cap.read()

        if not ret:
            break

        cheating = detector.detect_cheating(frame)

        for c in cheating:
            print(c)

        cv2.imshow("Camera", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()