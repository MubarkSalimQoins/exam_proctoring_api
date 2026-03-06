from app.services.face_service import FaceService
import cv2

# إنشاء خدمة التحقق من الوجه
service = FaceService()

# قراءة صورة الطالب (تأكد أن الصورة موجودة بنفس اسم 'test_face.jpg' في نفس المجلد)
frame = cv2.imread("test.jpg")

if frame is None:
    raise ValueError("❌ لم يتم العثور على الصورة test_face.jpg")

# تحقق من الطالب برقم معرفه (student_id=1 كمثال)
result = service.verify_student(frame, student_id=56)

print("نتيجة التحقق من الطالب:", result)