from langchain.prompts import StringPromptTemplate, PromptTemplate
from typing import List, Dict
import os
import logging
from dotenv import load_dotenv
load_dotenv()
logger = logging.getLogger(__name__)

try:
    from llama_cpp import Llama
except ImportError:
    Llama = None
    logger.error("llama-cpp-python is not installed. Please install it with 'pip install llama-cpp-python'.")

from datetime import datetime, timedelta
import re
from ..models.appointment import Appointment, AppointmentStatus
from ..models.user import User, UserRole
from ..models.doctor import Doctor
from sqlalchemy.orm import Session

class AppointmentAgent:
    def __init__(self, db: Session):
        self.db = db
        model_path = os.getenv("MISTRAL_MODEL_PATH", r"C:\\Users\\harsh\\.cache\\huggingface\\hub\\models--TheBloke--Mistral-7B-Instruct-v0.2-GGUF\\snapshots\\3a6fbf4a41a1d52e415a4958cde6856d34b2db93\\mistral-7b-instruct-v0.2.Q4_K_M.gguf")
        if not Llama:
            raise ImportError("llama-cpp-python is not installed.")
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Mistral 7B GGUF model not found at {model_path}")
        self.llm = Llama(model_path=model_path, n_ctx=2048)
        self.prompt = PromptTemplate(
            input_variables=["message"],
            template="""
            You are an intelligent appointment scheduling assistant. Your task is to help users schedule, modify, or cancel medical appointments.\n\nUser message: {message}\n\nPlease provide a helpful response that:\n1. Understands the user's intent\n2. Provides relevant information or next steps\n3. Maintains a professional and friendly tone\n\nResponse:\n"""
        )

    def generate_response(self, prompt: str) -> str:
        output = self.llm(prompt, max_tokens=256)
        return output["choices"][0]["text"] if "choices" in output and output["choices"] else str(output)

    async def process_message(self, message: str, user_id: int) -> str:
        try:
            logger.info(f"Processing message for user {user_id}: {message}")
            msg = message.lower()
            # --- USER CRUD ---
            if re.search(r"create user|add user|register user", msg):
                m = re.search(r"user ([a-zA-Z]+) ([a-zA-Z]+) with email ([^ ]+) and role ([A-Z]+)", msg)
                if m:
                    first_name, last_name, email, role = m.groups()
                    user = User(
                        email=email,
                        password="changeme",
                        first_name=first_name,
                        last_name=last_name,
                        role=UserRole[role],
                        is_active=True
                    )
                    self.db.add(user)
                    self.db.commit()
                    self.db.refresh(user)
                    return f"User {first_name} {last_name} created with email {email} and role {role}."
            if re.search(r"delete user", msg):
                m = re.search(r"delete user (\d+)", msg)
                if m:
                    user_id_del = int(m.group(1))
                    user = self.db.query(User).filter(User.id == user_id_del).first()
                    if user:
                        self.db.delete(user)
                        self.db.commit()
                        return f"User {user_id_del} deleted."
                    else:
                        return f"User {user_id_del} not found."
            if re.search(r"list users|show users|all users", msg):
                users = self.db.query(User).all()
                return "Users:\n" + "\n".join([f"{u.id}: {u.first_name} {u.last_name} ({u.role.value})" for u in users])
            # --- DOCTOR CRUD ---
            if re.search(r"create doctor|add doctor", msg):
                m = re.search(r"doctor ([a-zA-Z]+) ([a-zA-Z]+) with specialization ([^,]+), license ([^ ]+), user (\d+)", msg)
                if m:
                    first_name, last_name, specialization, license_number, user_id_doc = m.groups()
                    doctor = Doctor(
                        user_id=int(user_id_doc),
                        specialization=specialization.strip(),
                        license_number=license_number.strip()
                    )
                    self.db.add(doctor)
                    self.db.commit()
                    self.db.refresh(doctor)
                    return f"Doctor {first_name} {last_name} created with specialization {specialization}."
            if re.search(r"delete doctor", msg):
                m = re.search(r"delete doctor (\d+)", msg)
                if m:
                    doctor_id = int(m.group(1))
                    doctor = self.db.query(Doctor).filter(Doctor.id == doctor_id).first()
                    if doctor:
                        self.db.delete(doctor)
                        self.db.commit()
                        return f"Doctor {doctor_id} deleted."
                    else:
                        return f"Doctor {doctor_id} not found."
            if re.search(r"list doctors|show doctors|all doctors", msg):
                doctors = self.db.query(Doctor).all()
                return "Doctors:\n" + "\n".join([f"{d.id}: {d.specialization} (User {d.user_id})" for d in doctors])
            # --- APPOINTMENT CRUD ---
            if re.search(r"delete appointment", msg):
                m = re.search(r"delete appointment (\d+)", msg)
                if m:
                    apt_id = int(m.group(1))
                    apt = self.db.query(Appointment).filter(Appointment.id == apt_id).first()
                    if apt:
                        self.db.delete(apt)
                        self.db.commit()
                        return f"Appointment {apt_id} deleted."
                    else:
                        return f"Appointment {apt_id} not found."
            if re.search(r"list appointments|show appointments|all appointments", msg):
                apts = self.db.query(Appointment).all()
                return "Appointments:\n" + "\n".join([f"{a.id}: User {a.user_id}, Doctor {a.doctor_id}, {a.start_time.strftime('%Y-%m-%d %H:%M')}" for a in apts])
            if re.search(r"reschedule appointment", msg):
                m = re.search(r"reschedule appointment (\d+) to (\d{4}-\d{2}-\d{2}) (\d{1,2}):(\d{2})", msg)
                if m:
                    apt_id, date_str, hour, minute = m.groups()
                    apt = self.db.query(Appointment).filter(Appointment.id == int(apt_id)).first()
                    if apt:
                        new_start = datetime.strptime(f"{date_str} {hour}:{minute}", "%Y-%m-%d %H:%M")
                        apt.start_time = new_start
                        apt.end_time = new_start + timedelta(minutes=30)
                        self.db.commit()
                        self.db.refresh(apt)
                        return f"Appointment {apt_id} rescheduled to {new_start.strftime('%Y-%m-%d %I:%M %p')}."
                    else:
                        return f"Appointment {apt_id} not found."
            # --- fallback to LLM ---
            user_appointments = self.db.query(Appointment).filter(
                Appointment.user_id == user_id
            ).all()
            appointment_context = ""
            if user_appointments:
                appointment_context = "\nYour existing appointments:\n"
                for apt in user_appointments:
                    try:
                        doctor_name = f"Dr. {apt.doctor.user.last_name}" if apt.doctor and apt.doctor.user and hasattr(apt.doctor.user, 'last_name') else "(Unknown Doctor)"
                    except Exception as doc_ex:
                        logger.error(f"Error accessing doctor for appointment {apt.id}: {str(doc_ex)}")
                        doctor_name = "(Unknown Doctor)"
                    appointment_context += f"- {apt.start_time.strftime('%Y-%m-%d %H:%M')} with {doctor_name}: {apt.status.value}\n"

            booking_match = re.search(r"book|schedule|make an appointment", message, re.IGNORECASE)
            # Updated doctor regex to allow optional space after 'Dr.'
            doctor_match = re.search(r"Dr\.?\s*([A-Za-z]+)(?:\s+([A-Za-z]+))?", message)
            date_match = re.search(r"today|tomorrow|\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{2,4}", message, re.IGNORECASE)
            time_match = re.search(r"(\d{1,2})(?::(\d{2}))?\s*(a\.m\.|am|p\.m\.|pm)?", message, re.IGNORECASE)
            # Extract reason (e.g., 'for headache', 'for surgery', etc.)
            reason_match = re.search(r"for ([a-zA-Z0-9 ,\-]+)", message, re.IGNORECASE)
            reason = reason_match.group(1).strip() if reason_match else "Scheduled via agent"
            if booking_match and doctor_match and date_match and time_match:
                doctor_first = doctor_match.group(1)
                doctor_last = doctor_match.group(2) if doctor_match.group(2) else None
                doctor_user = None
                if doctor_last:
                    doctor_user = self.db.query(User).filter(
                        User.first_name.ilike(doctor_first),
                        User.last_name.ilike(doctor_last),
                        User.role == UserRole.DOCTOR
                    ).first()
                else:
                    doctor_user = self.db.query(User).filter(
                        User.last_name.ilike(doctor_first),
                        User.role == UserRole.DOCTOR
                    ).first()
                doctor_id = None
                if doctor_user:
                    doctor_profile = self.db.query(Doctor).filter_by(user_id=doctor_user.id).first()
                    if doctor_profile:
                        doctor_id = doctor_profile.id
                # Parse date
                if date_match.group(0).lower() == "tomorrow":
                    start_date = datetime.now() + timedelta(days=1)
                elif date_match.group(0).lower() == "today":
                    start_date = datetime.now()
                else:
                    try:
                        start_date = datetime.strptime(date_match.group(0), "%Y-%m-%d")
                    except Exception:
                        try:
                            start_date = datetime.strptime(date_match.group(0), "%d/%m/%Y")
                        except Exception:
                            start_date = None
                hour = int(time_match.group(1))
                minute = int(time_match.group(2) or 0)
                ampm = time_match.group(3)
                if ampm and ampm.lower().startswith('p') and hour < 12:
                    hour += 12
                if ampm and ampm.lower().startswith('a') and hour == 12:
                    hour = 0
                if start_date:
                    start_time = start_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
                    end_time = start_time + timedelta(minutes=30)
                else:
                    start_time = None
                    end_time = None
                # Check for missing doctor, date, or time
                if not doctor_id:
                    return "Sorry, I could not find the specified doctor. Please check the doctor's name."
                if not start_time or not end_time:
                    return "Sorry, I could not understand the date or time. Please specify in a clear format."
                # Check doctor's availability
                overlapping = self.db.query(Appointment).filter(
                    Appointment.doctor_id == doctor_id,
                    Appointment.start_time < end_time,
                    Appointment.end_time > start_time
                ).first()
                if overlapping:
                    return f"Sorry, Dr. {doctor_user.first_name} {doctor_user.last_name} is not available at that time. Please choose another slot."
                # Book the appointment
                new_appointment = Appointment(
                    user_id=user_id,
                    doctor_id=doctor_id,
                    start_time=start_time,
                    end_time=end_time,
                    reason=reason,
                    status=AppointmentStatus.PENDING
                )
                self.db.add(new_appointment)
                self.db.commit()
                self.db.refresh(new_appointment)
                logger.info(f"Created appointment: {new_appointment.id}")
                return f"Your appointment with Dr. {doctor_user.first_name} {doctor_user.last_name} is booked for {start_time.strftime('%Y-%m-%d %I:%M %p')} for {reason}."
            prompt = self.prompt.format(message=message + appointment_context)
            response = self.generate_response(prompt)
            logger.info(f"Generated response: {response}")
            return response
        except Exception as e:
            import traceback
            logger.error(f"Error processing request: {str(e)}")
            logger.error(traceback.format_exc())
            return f"I apologize, but I'm having trouble processing your request right now. Error: {str(e)}"
