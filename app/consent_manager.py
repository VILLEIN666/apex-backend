CONSENT_TEXT = """APEX SOVEREIGN V3 — PARENTAL CONTROL DISCLOSURE

এই অ্যাপ ইনস্টল করলে নিম্নলিখিত কাজ করবে:
• Device Administrator হিসেবে কাজ করবে (remote lock, wipe)
• প্রতি ৩০ সেকেন্ডে heartbeat পাঠাবে
• Location পড়বে (GPS + Network)
• Screen time track করবে
• Battery ও storage status পাঠাবে
• সব data TLS + AES-256 encrypt

আপনার অধিকার:
• Settings → Apps → APEX → Uninstall (সবসময়)
• Device Admin disable
• Unlink from guardian

এটি বাবা-মায়ের জন্য। সন্তানের বয়স < ১৮ হলে guardian-এর
লিখিত consent প্রয়োজন। কোনো লুকানো tracking নেই।
"""

def get_consent_text(): return CONSENT_TEXT
def get_consent_version(): return "1.0.0"
