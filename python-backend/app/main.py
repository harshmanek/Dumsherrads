from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from datetime import datetime
import logging
import traceback

from .database import SessionLocal, engine, Base
from .database.init_db import init_db
from .models import user, appointment
from .agent.appointment_agent import AppointmentAgent
from .routers import appointments, users, doctors, agent
from .routers import whisper as whisper_router
from .routers import auth as auth_router

dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(dotenv_path)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Appointment System API",
    description="API for managing medical appointments with an intelligent agent",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(agent.router, prefix="/agent", tags=["agent"])
app.include_router(appointments.router, prefix="/appointments", tags=["appointments"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(doctors.router, prefix="/doctors", tags=["doctors"])
app.include_router(whisper_router.router, prefix="/whisper", tags=["whisper"])
app.include_router(auth_router.router, prefix="/auth", tags=["auth"])

@app.on_event("startup")
async def startup_event():
    try:
        logger.info("Initializing database...")
        init_db()
        logger.info("Database initialization completed")
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        logger.error(traceback.format_exc())
        raise

@app.get("/")
async def root():
    return {"message": "Welcome to the Appointment System API"}

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}")
    logger.error(traceback.format_exc())
    return {"detail": str(exc)}, 500

