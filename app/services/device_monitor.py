import asyncio
from ..database import SessionLocal
from ..monitoring import scan_offline

async def background_scanner():
    while True:
        db = SessionLocal()
        try: scan_offline(db)
        finally: db.close()
        await asyncio.sleep(30)
