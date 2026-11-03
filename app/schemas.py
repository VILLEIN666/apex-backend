from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class GuardianCreate(BaseModel):
    email: str
    name: str
    password: str
    consent_accepted: bool

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class ChildOut(BaseModel):
    id: int
    child_name: str
    device_model: Optional[str] = None
    android_version: str
    is_paired: bool
    is_online: bool
    last_heartbeat: Optional[datetime]
    battery_level: int
    storage_free_mb: int
    storage_total_mb: int
    screen_time_minutes: int
    daily_limit_minutes: int
    last_lat: Optional[float]
    last_lon: Optional[float]
    class Config:
        from_attributes = True

class PairingInfo(BaseModel):
    pairing_token: str
    qr_url: str
    enroll_url: str

class PairRequest(BaseModel):
    pairing_token: str
    device_uid: str
    child_name: str
    device_model: str
    android_version: str
    consent_accepted: bool

class HeartbeatRequest(BaseModel):
    device_uid: str
    auth_token: str
    screen_time_minutes: Optional[int] = 0
    battery_level: Optional[int] = 0
    storage_free_mb: Optional[int] = 0
    storage_total_mb: Optional[int] = 0
