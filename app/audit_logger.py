from .models import AuditEvent
from .database import SessionLocal

def log_event(device_uid: str, event: str, detail: str = "", client_ts: int = 0):
    db = SessionLocal()
    try:
        db.add(AuditEvent(device_uid=device_uid, event=event,
                          detail=detail, client_ts=client_ts))
        db.commit()
    finally:
        db.close()
