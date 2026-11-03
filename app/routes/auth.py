from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime
from ..database import get_db
from ..models import Guardian, ConsentRecord
from ..schemas import GuardianCreate, Token
from ..security import hash_password, verify_password, create_access_token
from ..consent_manager import get_consent_text, get_consent_version

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register", response_model=Token)
def register(payload: GuardianCreate, request: Request, db: Session = Depends(get_db)):
    if not payload.consent_accepted:
        raise HTTPException(400, "Consent required")
    if db.query(Guardian).filter(Guardian.email == payload.email).first():
        raise HTTPException(400, "Email exists")
    g = Guardian(email=payload.email, name=payload.name,
                 hashed_password=hash_password(payload.password),
                 consent_version=get_consent_version(),
                 consent_accepted_at=datetime.utcnow())
    db.add(g); db.commit(); db.refresh(g)
    db.add(ConsentRecord(guardian_id=g.id, consent_text=get_consent_text(),
                         consent_version=get_consent_version(), accepted=True,
                         ip_address=request.client.host if request.client else ""))
    db.commit()
    return {"access_token": create_access_token({"sub": g.email})}

@router.post("/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    g = db.query(Guardian).filter(Guardian.email == form.username).first()
    if not g or not verify_password(form.password, g.hashed_password):
        raise HTTPException(401, "Wrong credentials")
    return {"access_token": create_access_token({"sub": g.email})}
