from pydantic import BaseModel
import os

class Settings(BaseModel):
    SECRET_KEY: str = os.getenv("APEX_SECRET", "APEX_V3_PARENTAL_CHANGE_ME_2026")
    MASTER_KEY: str = os.getenv("APEX_MASTER_KEY", "CHANGE_ME_32_BYTES_MIN_SECRET_V3")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30
    MAX_CHILDREN: int = 10
    DATABASE_URL: str = "sqlite:///./apex_v3.db"
    BASE_URL: str = os.getenv("APEX_BASE_URL", "http://localhost:8000")
    CONSENT_VERSION: str = "1.0.0"

settings = Settings()
