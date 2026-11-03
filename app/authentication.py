from .security import hash_password, verify_password, create_access_token

def register_guardian(email: str, name: str, password: str):
    return {"email": email, "name": name, "hash": hash_password(password)}

def login_guardian(email: str, password: str, db):
    from .models import Guardian
    g = db.query(Guardian).filter(Guardian.email==email).first()
    if not g or not verify_password(password, g.hashed_password): return None
    return create_access_token({"sub": g.email})
