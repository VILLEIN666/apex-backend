from datetime import datetime
from .models import Child

ONLINE_THRESHOLD_SECONDS = 90

def update_heartbeat(db, device_uid, auth_token, screen_time_min=0,
                     battery=0, storage_free=0, storage_total=0):
    c = db.query(Child).filter(Child.device_uid==device_uid).first()
    if not c or c.auth_token != auth_token: return None
    c.last_heartbeat = datetime.utcnow()
    c.is_online = True
    if screen_time_min: c.screen_time_minutes = screen_time_min
    if battery: c.battery_level = battery
    if storage_free: c.storage_free_mb = storage_free
    if storage_total: c.storage_total_mb = storage_total
    db.commit()
    return c

def scan_offline(db):
    now = datetime.utcnow()
    for c in db.query(Child).filter(Child.is_online==True).all():
        if c.last_heartbeat and (now - c.last_heartbeat).total_seconds() > ONLINE_THRESHOLD_SECONDS:
            c.is_online = False
    db.commit()
