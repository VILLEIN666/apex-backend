import secrets
from datetime import datetime
from .models import Child

def create_child(db, guardian_id, child_name):
    token = secrets.token_urlsafe(32)
    c = Child(guardian_id=guardian_id,
              device_uid=f"pending-{secrets.token_hex(6)}",
              child_name=child_name, pairing_token=token, is_paired=False)
    db.add(c); db.commit(); db.refresh(c)
    return c

def pair_child(db, pairing_token, device_uid, child_name, device_model, android_version):
    c = db.query(Child).filter(Child.pairing_token == pairing_token).first()
    if not c or c.is_paired: return None
    c.device_uid = device_uid
    c.child_name = child_name
    c.device_model = device_model
    c.android_version = android_version
    c.auth_token = secrets.token_urlsafe(48)
    c.is_paired = True
    c.paired_at = datetime.utcnow()
    c.last_heartbeat = datetime.utcnow()
    c.is_online = True
    db.commit()
    return c

def unlink_child(db, device_uid, auth_token):
    c = db.query(Child).filter(Child.device_uid==device_uid,
                                Child.auth_token==auth_token).first()
    if not c: return False
    c.is_paired = False; c.is_online = False; c.auth_token = None
    db.commit(); return True
