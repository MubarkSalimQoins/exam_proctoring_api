# from app.services.video_service import VideoMonitoringService

# monitor = VideoMonitoringService()

# monitor.start_monitoring(student_id=56)
# من اجل فحص الطلاب تشغيل الكيمرا من ملف فيديو ثم مقارنه الطلاب
from app.services.video_service import VideoMonitoringService

monitor = VideoMonitoringService()

monitor.start_monitoring()