from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Notification

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("/", response_model=List[dict])
def get_notifications(db: Session = Depends(get_db)):
    notifications = db.query(Notification).all()
    return [
        {
            "notification_id": notification.notification_id,
            "event_id": notification.event_id,
            "supervisor_id": notification.supervisor_id,
            "message": notification.message,
            "is_read": notification.is_read,
            "created_at": notification.created_at
        }
        for notification in notifications
    ]