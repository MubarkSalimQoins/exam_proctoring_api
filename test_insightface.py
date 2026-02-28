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
from insightface.app import FaceAnalysis
import cv2

app = FaceAnalysis(name="buffalo_l")
app.prepare(ctx_id=0)

img = cv2.imread("test.jpg")  # ضع صورة وجه في نفس المجلد
faces = app.get(img)

print("Number of faces:", len(faces))

if len(faces) > 0:
    embedding = faces[0].embedding
    print("Embedding length:", len(embedding))