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
# from app.services.audio_service import AudioService
# import time

# audio = AudioService()

# # تشغيل مراقبة الصوت
# audio.start()

# print("🎤 تكلم أو اصدر صوت قريب من المايكروفون")

# try:
#     while True:

#         event = audio.detect_noise()

#         if event:
#             print("🚨 تم اكتشاف صوت:", event)

#         time.sleep(1)

# except KeyboardInterrupt:
#     print("⏹ تم إيقاف الاختبار")

# audio.stop()
# -------------------------------------------------
# اختبر الايميل
# import smtplib
# from email.mime.text import MIMEText

# sender_email = "alqwynsnasr@gmail.com"
# password = "qigwuvrqwivyndxo"
# receiver_email = "mbarkalqwyns18@gmail.com"

# subject = "اختبار إرسال الإيميل"
# body = "تم إرسال هذا الإيميل بنجاح من نظام مراقبة الامتحانات."

# msg = MIMEText(body)
# msg["Subject"] = subject
# msg["From"] = sender_email
# msg["To"] = receiver_email

# try:
#     server = smtplib.SMTP("smtp.gmail.com", 587, timeout=30)
#     server.starttls()
#     server.login(sender_email, password)
#     server.sendmail(sender_email, receiver_email, msg.as_string())
#     server.quit()

#     print("✅ تم إرسال الإيميل بنجاح")

# except Exception as e:
#     print("❌ حدث خطأ:", e)
# ---------اختبار الصوت
# import os
# import winsound

# sound_path = os.path.join(os.path.dirname(__file__), "alarm.wav")

# print(sound_path)

# winsound.PlaySound(
#     sound_path,
#     winsound.SND_FILENAME
# )
# ------اختبار رقم ميكرفون
# import sounddevice as sd

# print(sd.query_devices())
# اختبار فريمات الكيمرا 
import cv2
import time

# رابط الكاميرا
rtsp_url = "rtsp://admin:TVSHZW@192.168.137.48:554/Streaming/Channels/101"

cap = cv2.VideoCapture(rtsp_url)

if not cap.isOpened():
    print("❌ Failed to connect to camera")
    exit()

print("🎥 Connected to camera... Measuring FPS")

frame_count = 0
start_time = time.time()

# قراءة 100 فريم
while frame_count < 100:
    ret, frame = cap.read()

    if not ret:
        print("❌ Failed to read frame")
        break

    frame_count += 1

end_time = time.time()

elapsed_time = end_time - start_time

if elapsed_time > 0:
    fps = frame_count / elapsed_time
    print(f"✅ Frames Read: {frame_count}")
    print(f"⏱ Time Taken: {elapsed_time:.2f} seconds")
    print(f"🎯 Actual FPS: {fps:.2f}")
else:
    print("❌ Error calculating FPS")

cap.release()
