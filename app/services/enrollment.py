import qrcode, io, base64
from ..config import settings

def generate_qr(pairing_token):
    enroll_url = f"{settings.BASE_URL}/enroll?token={pairing_token}"
    qr = qrcode.make(enroll_url)
    buf = io.BytesIO(); qr.save(buf, format="PNG")
    qr_b64 = base64.b64encode(buf.getvalue()).decode()
    return {"pairing_token": pairing_token,
            "qr_url": f"data:image/png;base64,{qr_b64}",
            "enroll_url": enroll_url}
