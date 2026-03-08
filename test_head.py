# # اختبار كود الحركه
# import cv2

# from app.services.head_pose_service import HeadPoseService

# detector = HeadPoseService()

# cap = cv2.VideoCapture(0)

# if not cap.isOpened():
#     print("❌ فشل فتح الكاميرا")
#     exit()

# print("🎥 الكاميرا تعمل - حرك رأسك للاختبار")

# while True:

#     ret, frame = cap.read()

#     if not ret:
#         break

#     cheating = detector.detect_head_pose(frame)

#     if cheating:
#         print("🚨 تم اكتشاف حالة:", cheating)

#     cv2.imshow("Head Pose Test", frame)

#     if cv2.waitKey(1) & 0xFF == 27:
#         break

# cap.release()
# cv2.destroyAllWindows()
# اختبار الصوت
from app.services.audio_service import AudioService
import time

audio = AudioService()

# تشغيل مراقبة الصوت
audio.start()

print("🎤 تكلم أو اصدر صوت قريب من المايكروفون")

try:
    while True:

        event = audio.detect_noise()

        if event:
            print("🚨 تم اكتشاف صوت:", event)

        time.sleep(1)

except KeyboardInterrupt:
    print("⏹ تم إيقاف الاختبار")

audio.stop()

