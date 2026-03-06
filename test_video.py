# from app.services.video_service import VideoMonitoringService

# monitor = VideoMonitoringService()

# monitor.start_monitoring(student_id=56)
from app.services.video_service import VideoMonitoringService

monitor = VideoMonitoringService()

monitor.start_monitoring()