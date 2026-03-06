# check_dependencies.py
try:
    import cv2
    import numpy as np
    import face_recognition
    import dlib
    import insightface
    import sqlalchemy
    print("✅ كل المكتبات مثبتة")
except ImportError as e:
    print("❌ مكتبة مفقودة:", e)

# فحص الخدمات
try:
    from app.services.face_service import FaceService
    from app.services.object_detection import ObjectDetectionService
    from app.services.head_pose_service import HeadPoseService
    from app.services.audio_service import AudioService
    print("✅ كل الخدمات موجودة")
except ImportError as e:
    print("❌ خدمة مفقودة أو خطأ في الاستيراد:", e)