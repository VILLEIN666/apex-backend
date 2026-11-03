from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from ..database import get_db
from ..models import Child, Command, Guardian
from ..security import get_current_guardian

router = APIRouter(prefix="/api/commands", tags=["commands"])

@router.post("/{child_id}/{command}")
def push_command(child_id: int, command: str,
                 guardian: Guardian = Depends(get_current_guardian),
                 db: Session = Depends(get_db)):
    c = db.query(Child).filter(Child.id==child_id,
                                Child.guardian_id==guardian.id).first()
    if not c: raise HTTPException(404)
    cmd = Command(child_id=child_id, command=command.upper())
    db.add(cmd); db.commit(); db.refresh(cmd)
    return {"command_id": cmd.id, "status": "queued"}

@router.get("/{child_id}/pending")
def pending(child_id: int, device_uid: str, auth_token: str,
            db: Session = Depends(get_db)):
    c = db.query(Child).filter(Child.id==child_id, Child.device_uid==device_uid,
                                Child.auth_token==auth_token).first()
    if not c: raise HTTPException(401)
    cmds = db.query(Command).filter(Command.child_id==child_id,
                                    Command.status=="pending").all()
    return [{"id": x.id, "command": x.command} for x in cmds]

@router.post("/ack/{command_id}")
def ack(command_id: int, status: str = "done", db: Session = Depends(get_db)):
    c = db.query(Command).filter(Command.id==command_id).first()
    if not c: raise HTTPException(404)
    c.status = status; c.executed_at = datetime.utcnow(); db.commit()
    return {"ok": True}
