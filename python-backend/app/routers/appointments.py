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
from ..auth import get_current_user

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

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[AppointmentRead])
async def get_appointments(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        # Only fetch appointments for the logged-in user
        appointments = db.query(Appointment).filter(Appointment.user_id == current_user.id).all()
        return appointments
    except Exception as e:
        logger.error(f"Error getting appointments: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{appointment_id}", response_model=AppointmentRead)
async def get_appointment(appointment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        return appointment
    except Exception as e:
        logger.error(f"Error getting appointment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=AppointmentRead)
async def create_appointment(appointment_data: AppointmentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        appointment = Appointment(
            user_id=appointment_data.user_id,
            doctor_id=appointment_data.doctor_id,
            start_time=appointment_data.start_time,
            end_time=appointment_data.end_time,
            reason=appointment_data.reason,
            status=AppointmentStatus(appointment_data.status)
        )
        db.add(appointment)
        db.commit()
        db.refresh(appointment)
        return appointment
    except Exception as e:
        logger.error(f"Error creating appointment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{appointment_id}", response_model=AppointmentRead)
async def update_appointment(appointment_id: int, appointment_data: AppointmentUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        update_dict = appointment_data.dict(exclude_unset=True)
        for key, value in update_dict.items():
            if hasattr(appointment, key):
                setattr(appointment, key, value)
        db.commit()
        db.refresh(appointment)
        return appointment
    except Exception as e:
        logger.error(f"Error updating appointment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{appointment_id}")
async def delete_appointment(appointment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        db.delete(appointment)
        db.commit()
        return {"message": "Appointment deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting appointment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
