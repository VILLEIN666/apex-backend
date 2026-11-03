from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import AuditEvent, Child, Guardian
from ..security import get_current_guardian

router = APIRouter(prefix="/api/audit", tags=["audit"])

@router.post("")
def write_event(payload: dict, db: Session = Depends(get_db)):
    db.add(AuditEvent(device_uid=payload.get("device_uid",""),
                      event=payload.get("event",""),
                      detail=payload.get("detail",""),
                      client_ts=payload.get("ts",0)))
    db.commit(); return {"ok": True}

@router.get("/{device_uid}")
def read_events(device_uid: str,
                guardian: Guardian = Depends(get_current_guardian),
                db: Session = Depends(get_db)):
    c = db.query(Child).filter(Child.device_uid==device_uid,
                                Child.guardian_id==guardian.id).first()
    if not c: return []
    return db.query(AuditEvent).filter(AuditEvent.device_uid==device_uid)\
        .order_by(AuditEvent.id.desc()).limit(200).all()
