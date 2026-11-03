from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Float, TypeDecorator, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base
from .encryption import encrypt, decrypt

class EncString(TypeDecorator):
    impl = String
    cache_ok = True
    def process_bind_param(self, v, d): return encrypt(v)
    def process_result_value(self, v, d): return decrypt(v)

class Guardian(Base):
    __tablename__ = "guardians"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(EncString)
    hashed_password = Column(String, nullable=False)
    consent_version = Column(String, default="1.0.0")
    consent_accepted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    children = relationship("Child", back_populates="guardian")

class Child(Base):
    __tablename__ = "children"
    id = Column(Integer, primary_key=True)
    guardian_id = Column(Integer, ForeignKey("guardians.id"))
    device_uid = Column(String, unique=True, index=True)
    child_name = Column(EncString)
    device_model = Column(EncString)
    android_version = Column(String, default="")
    pairing_token = Column(EncString, unique=True, index=True)
    auth_token = Column(EncString, unique=True, nullable=True)
    is_paired = Column(Boolean, default=False)
    is_online = Column(Boolean, default=False)
    last_heartbeat = Column(DateTime, nullable=True)
    paired_at = Column(DateTime, nullable=True)
    last_lat = Column(Float, nullable=True)
    last_lon = Column(Float, nullable=True)
    battery_level = Column(Integer, default=0)
    storage_free_mb = Column(Integer, default=0)
    storage_total_mb = Column(Integer, default=0)
    screen_time_minutes = Column(Integer, default=0)
    daily_limit_minutes = Column(Integer, default=180)
    created_at = Column(DateTime, default=datetime.utcnow)
    guardian = relationship("Guardian", back_populates="children")

class Command(Base):
    __tablename__ = "commands"
    id = Column(Integer, primary_key=True)
    child_id = Column(Integer, ForeignKey("children.id"))
    command = Column(String)
    payload = Column(Text, default="")
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    executed_at = Column(DateTime, nullable=True)

class AuditEvent(Base):
    __tablename__ = "audit_events"
    id = Column(Integer, primary_key=True)
    device_uid = Column(String, index=True)
    event = Column(String)
    detail = Column(Text, default="")
    client_ts = Column(Integer, default=0)
    server_ts = Column(DateTime, default=datetime.utcnow)

class ConsentRecord(Base):
    __tablename__ = "consent_records"
    id = Column(Integer, primary_key=True)
    guardian_id = Column(Integer, ForeignKey("guardians.id"))
    child_id = Column(Integer, ForeignKey("children.id"), nullable=True)
    consent_text = Column(Text)
    consent_version = Column(String)
    accepted = Column(Boolean, default=False)
    ip_address = Column(String, default="")
    accepted_at = Column(DateTime, default=datetime.utcnow)
