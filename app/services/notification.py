def send_push(fcm_token, title, body, data=None):
    print(f"[PUSH] {title}: {body} → {fcm_token[:16] if fcm_token else 'none'}")

def send_email(to, subject, body):
    print(f"[EMAIL] {subject} → {to}")
