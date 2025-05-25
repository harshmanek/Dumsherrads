from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from datetime import datetime
from pydantic import BaseModel
from ..database import SessionLocal
from ..models.appointment import Appointment, AppointmentStatus
from ..models.user import User, UserRole
from ..models.doctor import Doctor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic models
class AppointmentCreate(BaseModel):
    user_id: int
    doctor_id: int
    start_time: datetime
    end_time: datetime
    reason: str
    status: str = "PENDING"

    class Config:
        use_enum_values = True

class AppointmentUpdate(BaseModel):
    reason: Optional[str] = None
    status: Optional[str] = None

    class Config:
        use_enum_values = True

class AppointmentRead(BaseModel):
    id: int
    user_id: int
    doctor_id: int
    start_time: datetime
    end_time: datetime
    reason: str
    status: str
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
