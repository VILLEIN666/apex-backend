from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import bcrypt
from .config import settings
from .database import get_db
from .models import Guardian

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def _prepare_password(password: str) -> bytes:
    """bcrypt-এর 72-byte hard limit এ truncate (security-safe)"""
    pw = password.encode("utf-8")
    if len(pw) > 72:
        pw = pw[:72]
    return pw


def hash_password(p: str) -> str:
    return bcrypt.hashpw(_prepare_password(p), bcrypt.gensalt()).decode()


def verify_password(p: str, h: str) -> bool:
    try:
        return bcrypt.checkpw(_prepare_password(p), h.encode())
    except Exception:
        return False


def create_access_token(data):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def get_current_guardian(token: str = Depends(oauth2_scheme),
                         db: Session = Depends(get_db)) -> Guardian:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        raise HTTPException(401, "Invalid token")
    g = db.query(Guardian).filter(Guardian.email == payload.get("sub")).first()
    if not g:
        raise HTTPException(401, "Not found")
    return g
