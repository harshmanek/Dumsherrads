from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
import logging
from pydantic import BaseModel
from ..database import SessionLocal
from ..models.user import User, UserRole
from ..models.doctor import Doctor
from ..auth import get_current_user

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic models
class DoctorCreate(BaseModel):
    user_id: int
    specialization: str
    license_number: str

class DoctorUpdate(BaseModel):
    specialization: str | None = None
    license_number: str | None = None

class DoctorRead(BaseModel):
    id: int
    user_id: int
    specialization: str
    license_number: str

    class Config:
        orm_mode = True

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[DoctorRead])
async def get_doctors(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get all doctors"""
    try:
        doctors = db.query(Doctor).all()
        return doctors
    except Exception as e:
        logger.error(f"Error getting doctors: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{doctor_id}", response_model=DoctorRead)
async def get_doctor(doctor_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get a doctor by ID"""
    try:
        doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")
        return doctor
    except Exception as e:
        logger.error(f"Error getting doctor: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=DoctorRead)
async def create_doctor(doctor_data: DoctorCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Create a new doctor profile"""
    try:
        # Validate user exists and is a doctor
        user = db.query(User).filter(User.id == doctor_data.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if user.role != UserRole.DOCTOR:
            raise HTTPException(status_code=400, detail="User must have DOCTOR role")
        # Check if doctor profile already exists
        existing_doctor = db.query(Doctor).filter(Doctor.user_id == doctor_data.user_id).first()
        if existing_doctor:
            raise HTTPException(status_code=400, detail="Doctor profile already exists")
        # Create doctor profile
        doctor = Doctor(
            user_id=doctor_data.user_id,
            specialization=doctor_data.specialization,
            license_number=doctor_data.license_number
        )
        db.add(doctor)
        db.commit()
        db.refresh(doctor)
        return doctor
    except Exception as e:
        logger.error(f"Error creating doctor: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{doctor_id}", response_model=DoctorRead)
async def update_doctor(doctor_id: int, doctor_data: DoctorUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Update a doctor profile"""
    try:
        doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")
        # Update fields
        update_dict = doctor_data.dict(exclude_unset=True)
        for key, value in update_dict.items():
            if hasattr(doctor, key):
                setattr(doctor, key, value)
        db.commit()
        db.refresh(doctor)
        return doctor
    except Exception as e:
        logger.error(f"Error updating doctor: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{doctor_id}")
async def delete_doctor(doctor_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Delete a doctor profile"""
    try:
        doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")
        db.delete(doctor)
        db.commit()
        return {"message": "Doctor profile deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting doctor: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
