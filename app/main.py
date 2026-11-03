from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse, HTMLResponse
from .database import Base, engine, SessionLocal
from .routes import auth, devices, commands, audit, consent
from .models import Child
from .services.device_monitor import background_scanner
import os, asyncio, json

Base.metadata.create_all(bind=engine)
app = FastAPI(title="APEX SOVEREIGN V3 — Parental", version="3.0")
app.include_router(auth.router)
app.include_router(devices.router)
app.include_router(commands.router)
app.include_router(audit.router)
app.include_router(consent.router)

templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
async def startup():
    asyncio.create_task(background_scanner())

# ============ TEMPLATE HELPERS ============
def render(request, template, ctx=None):
    """Starlette 1.x compatible template render"""
    return templates.TemplateResponse(request, template, ctx or {})

# ============ ROUTES ============
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return render(request, "index.html")

@app.get("/enroll", response_class=HTMLResponse)
def enroll(request: Request, token: str = ""):
    return render(request, "enroll.html", {"token": token})

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    return render(request, "dashboard.html")

@app.get("/api/apk/device")
def download_apk():
    p = "apk/apex-parental.apk"
    if not os.path.exists(p):
        return {"error": "APK not built yet — see Part 3"}
    return FileResponse(p, media_type="application/vnd.android.package-archive",
                        filename="apex-parental.apk")

# ============ WEBSOCKET ============
@app.websocket("/ws/devices")
async def ws_devices(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            db = SessionLocal()
            children = db.query(Child).filter(Child.is_paired==True).all()
            data = [{
                "id": c.id, "name": c.child_name or "?",
                "model": c.device_model or "?", "online": c.is_online,
                "last_hb": c.last_heartbeat.isoformat() if c.last_heartbeat else None,
                "screen_time": c.screen_time_minutes,
                "limit": c.daily_limit_minutes,
                "battery": c.battery_level,
                "storage_free": c.storage_free_mb,
                "storage_total": c.storage_total_mb,
                "lat": c.last_lat, "lon": c.last_lon
            } for c in children]
            db.close()
            await ws.send_text(json.dumps(data))
            await asyncio.sleep(3)
    except WebSocketDisconnect:
        pass
