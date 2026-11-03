from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from ..database import get_db
from ..models import Child, Guardian
from ..schemas import ChildOut, PairingInfo, PairRequest, HeartbeatRequest
from ..security import get_current_guardian
from ..device_manager import create_child, pair_child, unlink_child
from ..monitoring import update_heartbeat
from ..services.enrollment import generate_qr
from ..config import settings

router = APIRouter(prefix="/api/devices", tags=["devices"])

@router.post("/create-pairing", response_model=PairingInfo)
def create_pairing(child_name: str = "New Child",
                   guardian: Guardian = Depends(get_current_guardian),
                   db: Session = Depends(get_db)):
    count = db.query(Child).filter(Child.guardian_id==guardian.id).count()
    if count >= settings.MAX_CHILDREN:
        raise HTTPException(400, f"Limit {settings.MAX_CHILDREN} reached")
    c = create_child(db, guardian.id, child_name)
    return generate_qr(c.pairing_token)

@router.get("", response_model=list[ChildOut])
def list_children(guardian: Guardian = Depends(get_current_guardian),
                  db: Session = Depends(get_db)):
    return db.query(Child).filter(Child.guardian_id==guardian.id).all()

@router.delete("/{child_id}")
def delete_child(child_id: int,
                 guardian: Guardian = Depends(get_current_guardian),
                 db: Session = Depends(get_db)):
    c = db.query(Child).filter(Child.id==child_id,
                                Child.guardian_id==guardian.id).first()
    if not c: raise HTTPException(404)
    db.delete(c); db.commit(); return {"ok": True}

@router.post("/pair")
def pair_device(payload: PairRequest, db: Session = Depends(get_db)):
    if not payload.consent_accepted:
        raise HTTPException(400, "Consent required on device")
    c = pair_child(db, payload.pairing_token, payload.device_uid,
                   payload.child_name, payload.device_model, payload.android_version)
    if not c: raise HTTPException(400, "Invalid or already paired")
    return {"auth_token": c.auth_token, "device_id": c.id, "status": "paired"}

@router.post("/heartbeat")
def heartbeat(payload: HeartbeatRequest, db: Session = Depends(get_db)):
    c = update_heartbeat(db, payload.device_uid, payload.auth_token,
                         payload.screen_time_minutes or 0,
                         payload.battery_level or 0,
                         payload.storage_free_mb or 0,
                         payload.storage_total_mb or 0)
    if not c: raise HTTPException(401, "Unauthorized")
    return {"status": "alive", "server_time": datetime.utcnow().isoformat()}

@router.post("/unlink")
def unlink(payload: dict, db: Session = Depends(get_db)):
    if not unlink_child(db, payload.get("device_uid",""), payload.get("auth_token","")):
        raise HTTPException(401)
    return {"ok": True}

@router.post("/locate")
def locate(payload: dict, db: Session = Depends(get_db)):
    c = db.query(Child).filter(Child.device_uid==payload.get("device_uid"),
                                Child.auth_token==payload.get("auth_token")).first()
    if not c: raise HTTPException(401)
    c.last_lat = payload.get("lat"); c.last_lon = payload.get("lon")
    db.commit(); return {"ok": True}

# ============ SCREEN STREAMING ============
import os, base64
from fastapi.responses import FileResponse

FRAME_DIR = "frames"
os.makedirs(FRAME_DIR, exist_ok=True)

@router.post("/frame")
def receive_frame(payload: dict, db: Session = Depends(get_db)):
    dev = db.query(Child).filter(
        Child.device_uid == payload.get("device_uid"),
        Child.auth_token == payload.get("auth_token")
    ).first()
    if not dev:
        raise HTTPException(401, "Unauthorized")

    b64 = payload.get("image_b64")
    if not b64:
        raise HTTPException(400, "Missing image")

    try:
        img_bytes = base64.b64decode(b64)
        frame_path = os.path.join(FRAME_DIR, f"device_{dev.id}.jpg")
        with open(frame_path, "wb") as f:
            f.write(img_bytes)
        from datetime import datetime
        dev.last_heartbeat = datetime.utcnow()
        dev.is_online = True
        db.commit()
        return {"ok": True, "size": len(img_bytes)}
    except Exception as e:
        raise HTTPException(500, str(e))


@router.get("/{child_id}/frame")
def get_latest_frame(child_id: int,
                     guardian: Guardian = Depends(get_current_guardian),
                     db: Session = Depends(get_db)):
    c = db.query(Child).filter(
        Child.id == child_id,
        Child.guardian_id == guardian.id
    ).first()
    if not c:
        raise HTTPException(404)

    frame_path = os.path.join(FRAME_DIR, f"device_{child_id}.jpg")
    if not os.path.exists(frame_path):
        raise HTTPException(404, "No frame yet")
    return FileResponse(frame_path, media_type="image/jpeg")
