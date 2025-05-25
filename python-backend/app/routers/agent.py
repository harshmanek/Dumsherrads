from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict
import logging
from pydantic import BaseModel
from ..database import SessionLocal
from ..agent.appointment_agent import AppointmentAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic models
class ChatRequest(BaseModel):
    message: str
    user_id: int

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/chat")
async def chat_with_agent(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Chat with the appointment agent
    """
    try:
        logger.info(f"Received chat request: {request}")
        agent = AppointmentAgent(db)
        response = await agent.process_message(request.message, request.user_id)
        logger.info(f"Agent response: {response}")
        return {"response": response}
    except Exception as e:
        logger.error(f"Error in chat endpoint:) {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 