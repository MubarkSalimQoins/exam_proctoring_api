# نظام كشف الغش في الامتحانات

نظام ذكي لكشف محاولات الغش في الامتحانات باستخدام FastAPI و MySQL.

## المتطلبات

- Python 3.8+
- MySQL Server
- pip

## التثبيت

1. تثبيت المتطلبات:
```bash
pip install -r requirements.txt
```

2. إعداد قاعدة البيانات:
   - أنشئ قاعدة بيانات MySQL جديدة
   - حدث ملف `.env` بمعلومات الاتصال

3. تشغيل التطبيق:
```bash
python main.py
```

## إعداد قاعدة البيانات

تأكد من وجود الجداول التالية في قاعدة البيانات:

### جدول students
```sql
CREATE TABLE students (
    id INT PRIMARY KEY AUTO_INCREMENT,
    full_name VARCHAR(255) NOT NULL,
    registration_number VARCHAR(50) UNIQUE NOT NULL,
    major VARCHAR(100) NOT NULL,
    level VARCHAR(50) NOT NULL,
    student_image TEXT
);
```

### جدول cheating_types
```sql
CREATE TABLE cheating_types (
    id INT PRIMARY KEY AUTO_INCREMENT,
    type_name VARCHAR(100) UNIQUE NOT NULL
);
```

### جدول cheating_events
```sql
CREATE TABLE cheating_events (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    type_id INT NOT NULL,
    event_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    similarity FLOAT NOT NULL,
    video_clip TEXT,
    image_snapshot TEXT,
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (type_id) REFERENCES cheating_types(id)
);
```

### جدول notifications
```sql
CREATE TABLE notifications (
    id INT PRIMARY KEY AUTO_INCREMENT,
    event_id INT NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    notification_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES cheating_events(id)
);
```

## استخدام API

### تسجيل حدث غش
```bash
POST /api/cheating/detect
{
    "student_id": 1,
    "type_id": 1,
    "similarity": 0.85,
    "video_clip": "path/to/video.mp4",
    "image_snapshot": "path/to/image.jpg"
}
```

### الحصول على أحداث الغش لطالب
```bash
GET /api/cheating/events/{student_id}
```

## الوثائق

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc