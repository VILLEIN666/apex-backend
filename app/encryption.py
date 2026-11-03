from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64, hashlib, os
from .config import settings

# 32-byte key from MASTER_KEY
_key = hashlib.sha256(settings.MASTER_KEY.encode()).digest()

def encrypt(v):
    if v is None:
        return None
    plaintext = str(v).encode()
    iv = os.urandom(16)
    cipher = AES.new(_key, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(plaintext, 16))
    return base64.b64encode(iv + ciphertext).decode()

def decrypt(v):
    if v is None:
        return None
    try:
        raw = base64.b64decode(v.encode())
        if len(raw) < 32:
            return v  # not encrypted (legacy/plain)
        iv, ciphertext = raw[:16], raw[16:]
        cipher = AES.new(_key, AES.MODE_CBC, iv)
        return unpad(cipher.decrypt(ciphertext), 16).decode()
    except Exception:
        return v  # fallback: unencrypted / already plain
