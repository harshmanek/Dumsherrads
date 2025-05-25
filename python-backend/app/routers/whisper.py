from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from sqlalchemy.orm import Session
import whisper
import tempfile
from ..database import SessionLocal
from .agent import router as agent_router
from ..agent.appointment_agent import AppointmentAgent

router = APIRouter()

@router.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    try:
        model = whisper.load_model("base")  # or "small", "medium", "large"
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name
        result = model.transcribe(tmp_path)
        return {"transcription": result["text"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/voice-agent")
async def voice_agent_reply(
    file: UploadFile = File(...),
    user_id: int = Form(...),
    db: Session = Depends(lambda: SessionLocal())
):
    try:
        model = whisper.load_model("base")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name
        result = model.transcribe(tmp_path)
        transcription = result["text"]
        agent = AppointmentAgent(db)
        agent_reply = await agent.process_message(transcription, user_id)
        return {"transcription": transcription, "agent_reply": agent_reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
