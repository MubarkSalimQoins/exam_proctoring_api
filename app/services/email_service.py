# import smtplib
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText
# from email.mime.base import MIMEBase
# from email import encoders
# import os


# class EmailService:

#     def __init__(self):

#         # بيانات البريد
#         self.smtp_server = "smtp.gmail.com"
#         self.smtp_port = 587

#         # بريد النظام
#         self.sender_email = "alqwynsnasr@gmail.com"

#         # كلمة مرور التطبيق (App Password)
#         self.password = "qigwuvrqwivyndxo"

#         # بريد المشرف
#         self.supervisor_email = "mbarkalqwyns18@gmail.com"


#     def send_cheating_alert(
#         self,
#         student_id,
#         cheating_type,
#         confidence,
#         snapshot_path=None,
#         video_path=None
#     ):

#         try:

#             subject = "🚨 تنبيه حالة غش في الامتحان"

#             body = f"""
# تم اكتشاف حالة غش أثناء الامتحان

# رقم الطالب: {student_id}

# نوع الغش: {cheating_type}

# نسبة الثقة: {confidence}

# تم تسجيل الحالة في النظام.
# """

#             msg = MIMEMultipart()

#             msg["From"] = self.sender_email
#             msg["To"] = self.supervisor_email
#             msg["Subject"] = subject

#             msg.attach(MIMEText(body, "plain"))

#             # إرفاق صورة
#             if snapshot_path and os.path.exists(snapshot_path):

#                 with open(snapshot_path, "rb") as f:

#                     part = MIMEBase("application", "octet-stream")
#                     part.set_payload(f.read())

#                 encoders.encode_base64(part)

#                 part.add_header(
#                     "Content-Disposition",
#                     f"attachment; filename={os.path.basename(snapshot_path)}"
#                 )

#                 msg.attach(part)

#             # إرفاق فيديو
#             if video_path and os.path.exists(video_path):

#                 with open(video_path, "rb") as f:

#                     part = MIMEBase("application", "octet-stream")
#                     part.set_payload(f.read())

#                 encoders.encode_base64(part)

#                 part.add_header(
#                     "Content-Disposition",
#                     f"attachment; filename={os.path.basename(video_path)}"
#                 )

#                 msg.attach(part)

#             # الاتصال بالسيرفر
#             server = smtplib.SMTP(self.smtp_server, self.smtp_port)
#             server.starttls()

#             server.login(self.sender_email, self.password)

#             server.send_message(msg)

#             server.quit()

#             print("📧 تم إرسال تنبيه الغش عبر الإيميل")

#         except Exception as e:

#             print("❌ فشل إرسال البريد:", e)
# # --------------------------------------------------------
import smtplib
import os
import time

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


class EmailService:

    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587

        # بريد النظام
        self.sender_email = "alqwynsnasr@gmail.com"

        # App Password
        self.password = "qigwuvrqwivyndxo"

        # بريد المشرف
        self.supervisor_email = "mbarkalqwyns18@gmail.com"

    def send_cheating_alert(
        self,
        student_name,
        student_number,
        cheating_type,
        confidence,
        snapshot_path=None,
        video_path=None
    ):

        subject = "🚨 تنبيه: اكتشاف حالة غش"

        body = f"""
        <h2 style="color:red;">🚨  تم اكتشاف حالة غش يرجى مراجعة لوحه التحكم</h2>

        <p><b>اسم الطالب:</b> {student_name}</p>
        <p><b>رقم الطالب:</b> {student_number}</p>
        <p><b>نوع الغش:</b> {cheating_type}</p>
        <p><b>نسبة الثقة:</b> {confidence}%</p>

        <hr>

        <p>تم تسجيل الحالة في نظام مراقبة الامتحانات.</p>
        """

        msg = MIMEMultipart()
        msg["From"] = self.sender_email
        msg["To"] = self.supervisor_email
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "html"))

        # تم تعطيل إرفاق الصورة والفيديو لمنع إرسال أي مرفقات
        """
        # 📷 إرفاق صورة
        if snapshot_path and os.path.exists(snapshot_path):
            with open(snapshot_path, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename={os.path.basename(snapshot_path)}"
            )
            msg.attach(part)

        # 🎥 إرفاق فيديو
        if video_path and os.path.exists(video_path):
            with open(video_path, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename={os.path.basename(video_path)}"
            )
            msg.attach(part)
        """

        # 📧 إرسال الإيميل مع إعادة المحاولة
        for attempt in range(3):
            try:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30)
                server.starttls()
                server.login(self.sender_email, self.password)
                server.send_message(msg)
                server.quit()
                print("📧 تم إرسال تنبيه الغش عبر الإيميل (بدون مرفقات)")
                break
            except Exception as e:
                print("❌ فشل الإرسال، إعادة المحاولة...", e)
                time.sleep(5)