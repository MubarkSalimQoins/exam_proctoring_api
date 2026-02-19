# from fastapi import APIRouter, Depends
# from sqlalchemy.orm import Session
# from pydantic import BaseModel
# from typing import List, Optional, Literal
# from datetime import datetime

# from app.database import get_db
# from app.models import CheatingEvent, Notification

# router = APIRouter(prefix="/cheating-events", tags=["Cheating Events"])

# class CheatingEventCreate(BaseModel):
#     student_id: int
#     cheating_type_id: int
#     status: Literal["suspected", "confirmed", "rejected"]
#     confidence_score: float
#     snapshot_path: Optional[str] = None
#     video_path: Optional[str] = None
#     event_time: Optional[datetime] = None


# @router.post("/")
# def create_cheating_event(event: CheatingEventCreate, db: Session = Depends(get_db)):
#     db_event = CheatingEvent(
#         student_id=event.student_id,
#         cheating_type_id=event.cheating_type_id,
#         status=event.status,
#         confidence_score=event.confidence_score,
#         snapshot_path=event.snapshot_path,
#         video_path=event.video_path,
#         event_time=event.event_time or datetime.now(),
#         created_at=datetime.now()
#     )
#     db.add(db_event)
#     db.commit()
#     db.refresh(db_event)

#     notification = Notification(
#         event_id=db_event.event_id,
#         supervisor_id=1,  # مؤقتًا
#         message=f"Cheating event detected for student {event.student_id}",
#         is_read=False,
#         created_at=datetime.now()
#     )
#     db.add(notification)
#     db.commit()

#     return {
#         "event_id": db_event.event_id,
#         "message": "Event created successfully"
#     }


# @router.get("/{student_id}", response_model=List[dict])
# def get_student_cheating_events(student_id: int, db: Session = Depends(get_db)):
#     events = db.query(CheatingEvent).filter(
#         CheatingEvent.student_id == student_id
#     ).all()

#     return [
#         {
#             "event_id": event.event_id,
#             "student_id": event.student_id,
#             "cheating_type_id": event.cheating_type_id,
#             "status": event.status,
#             "confidence_score": event.confidence_score,
#             "snapshot_path": event.snapshot_path,
#             "video_path": event.video_path,
#             "event_time": event.event_time,
#             "created_at": event.created_at
#         }
#         for event in events
#     ]
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Literal
from datetime import datetime

from app.database import get_db
from app.models import CheatingEvent, Notification

router = APIRouter(
    prefix="/cheating-events",
    tags=["Cheating Events"]
)

# ===== Schema =====
class CheatingEventCreate(BaseModel):
    student_id: int
    cheating_type_id: int
    status: Literal["suspected", "confirmed", "rejected"]
    confidence_score: float
    snapshot_path: Optional[str] = None
    video_path: Optional[str] = None
    # ❌ لا نأخذ الوقت من المستخدم
    # event_time يحسبه النظام تلقائيًا


# ===== Create Cheating Event =====
@router.post("/")
def create_cheating_event(
    event: CheatingEventCreate,
    db: Session = Depends(get_db)
):
    try:
        db_event = CheatingEvent(
            student_id=event.student_id,
            cheating_type_id=event.cheating_type_id,
            status=event.status,
            confidence_score=event.confidence_score,
            snapshot_path=event.snapshot_path,
            video_path=event.video_path,
            event_time=datetime.now()
        )

        db.add(db_event)
        db.commit()
        db.refresh(db_event)

        # إنشاء إشعار
        notification = Notification(
            event_id=db_event.event_id,
            supervisor_id=1,  # مؤقتًا (نربطه لاحقًا بالمشرف الحقيقي)
            message=f"تم رصد حالة غش للطالب رقم {event.student_id}",
            is_read=False
        )

        db.add(notification)
        db.commit()

        return {
            "event_id": db_event.event_id,
            "message": "تم تسجيل حالة الغش بنجاح"
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ===== Get Student Cheating Events =====
@router.get("/{student_id}")
def get_student_cheating_events(
    student_id: int,
    db: Session = Depends(get_db)
):
    events = (
        db.query(CheatingEvent)
        .filter(CheatingEvent.student_id == student_id)
        .all()
    )

    return [
        {
            "event_id": event.event_id,
            "student_id": event.student_id,
            "cheating_type_id": event.cheating_type_id,
            "status": event.status,
            "confidence_score": float(event.confidence_score) if event.confidence_score else None,
            "snapshot_path": event.snapshot_path,
            "video_path": event.video_path,
            "event_time": event.event_time,
            "created_at": event.created_at
        }
        for event in events
    ]
