from fastapi import APIRouter
from ..consent_manager import get_consent_text, get_consent_version

router = APIRouter(prefix="/api/consent", tags=["consent"])

@router.get("")
def current_consent():
    return {"version": get_consent_version(), "text": get_consent_text()}
