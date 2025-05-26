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
from dateutil import parser as date_parser
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
            You are an intelligent appointment scheduling assistant. Your task is to help users schedule, modify, or cancel medical appointments.\n\nUser message: {message}\n\nPlease provide a helpful response that:\n1. Understands the user's intent\n2. Provides relevant information or next steps\n3. Maintains a professional and friendly tone\n\nResponse:\n. dont use phrase like you will receive updates via email or text message, just say that you will notify them when the appointment is confirmed"""
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
            # --- RESCHEDULE BY APPOINTMENT ID (NATURAL LANGUAGE) ---
            change_by_id_match = re.search(
                r'(?:change|reschedul(?:e|ing|ed|ule|uled|uling|ul|ule)?) appointment (\d+) to ([^\n]+)',
                msg, re.IGNORECASE
            )
            if change_by_id_match:
                apt_id = int(change_by_id_match.group(1))
                new_time_str = change_by_id_match.group(2)
                appointment = self.db.query(Appointment).filter(Appointment.id == apt_id, Appointment.user_id == user_id).first()
                if not appointment:
                    return f"Appointment {apt_id} not found."
                try:
                    new_start = date_parser.parse(new_time_str, fuzzy=True, dayfirst=True)
                except Exception:
                    return "Sorry, I could not understand the new date and time. Please specify clearly."
                if new_start.year == 1900:
                    new_start = appointment.start_time.replace(hour=new_start.hour, minute=new_start.minute, second=0, microsecond=0)
                new_end = new_start + timedelta(minutes=30)
                overlapping = self.db.query(Appointment).filter(
                    Appointment.doctor_id == appointment.doctor_id,
                    Appointment.id != appointment.id,
                    Appointment.start_time < new_end,
                    Appointment.end_time > new_start
                ).first()
                if overlapping:
                    return "Sorry, the doctor is not available at that time. Please choose another slot."
                appointment.start_time = new_start
                appointment.end_time = new_end
                self.db.commit()
                self.db.refresh(appointment)
                return f"Appointment {apt_id} has been rescheduled to {new_start.strftime('%Y-%m-%d %I:%M %p')}."
            # --- APPOINTMENT LISTING (NATURAL LANGUAGE) ---
            list_appt_match = re.search(r"(show|list|display|what are|which are|my|all)? ?(upcoming|current|future|pending|confirmed|cancelled|completed)? ?appointments", msg)
            if list_appt_match:
                status_filter = list_appt_match.group(2)
                query = self.db.query(Appointment).filter(Appointment.user_id == user_id)
                if status_filter:
                    try:
                        status_enum = AppointmentStatus[status_filter.upper()]
                        query = query.filter(Appointment.status == status_enum)
                    except Exception:
                        pass
                appointments = query.order_by(Appointment.start_time.asc()).all()
                if not appointments:
                    return "You have no appointments matching your request."
                lines = []
                for apt in appointments:
                    doctor_name = f"Dr. {apt.doctor.user.first_name} {apt.doctor.user.last_name}" if apt.doctor and apt.doctor.user else "(Unknown Doctor)"
                    lines.append(f"ID: {apt.id} | {apt.start_time.strftime('%Y-%m-%d %I:%M %p')} with {doctor_name} | Status: {apt.status.value}")
                return "Your appointments:\n" + "\n".join(lines)
            # --- NATURAL LANGUAGE CANCEL/DELETE (IMPROVED AMBIGUITY HANDLING) ---
            delete_or_cancel_match = re.search(r"(delete|cancel) my appointment with dr\.?\s*([A-Za-z]+)(?:\s+([A-Za-z]+))?(?: of| for| on| at)? ([^\n]*)", msg, re.IGNORECASE)
            logger.info(f"Regex match for delete/cancel: {delete_or_cancel_match}")
            if delete_or_cancel_match:
                action = delete_or_cancel_match.group(1).lower()
                doctor_first = delete_or_cancel_match.group(2)
                doctor_last = delete_or_cancel_match.group(3) if delete_or_cancel_match.group(3) else None
                date_str = delete_or_cancel_match.group(4).strip()
                # Find doctor user
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
                if not doctor_user:
                    return "Sorry, I could not find the specified doctor. Please check the doctor's name."
                doctor_profile = self.db.query(Doctor).filter_by(user_id=doctor_user.id).first()
                if not doctor_profile:
                    return "Sorry, I could not find the doctor's profile."
                # Parse date (default to today/tomorrow if mentioned)
                appt_date = None
                if date_str:
                    try:
                        appt_date = date_parser.parse(date_str, fuzzy=True, dayfirst=True).date()
                    except Exception:
                        appt_date = None
                if not appt_date:
                    if "tomorrow" in msg:
                        appt_date = (datetime.now() + timedelta(days=1)).date()
                    else:
                        appt_date = None
                # Find user's appointments with this doctor (optionally on that date)
                query = self.db.query(Appointment).filter(
                    Appointment.user_id == user_id,
                    Appointment.doctor_id == doctor_profile.id,
                    Appointment.status.in_([AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED])
                )
                if appt_date:
                    query = query.filter(
                        Appointment.start_time >= datetime.combine(appt_date, datetime.min.time()),
                        Appointment.start_time <= datetime.combine(appt_date, datetime.max.time())
                    )
                matches = query.order_by(Appointment.start_time.asc()).all()
                if not matches:
                    return f"No appointment found with Dr. {doctor_user.last_name}" + (f" on {appt_date.strftime('%Y-%m-%d')}" if appt_date else ".")
                if len(matches) > 1:
                    lines = []
                    for apt in matches:
                        lines.append(f"ID: {apt.id} | {apt.start_time.strftime('%Y-%m-%d %I:%M %p')} | Status: {apt.status.value}")
                    return "Multiple appointments found. Please specify the appointment ID to cancel/delete:\n" + "\n".join(lines)
                appointment = matches[0]
                if action == "delete":
                    self.db.delete(appointment)
                    self.db.commit()
                    return f"Your appointment with Dr. {doctor_user.first_name} {doctor_user.last_name} on {appointment.start_time.strftime('%Y-%m-%d %I:%M %p')} has been deleted."
                else:
                    appointment.status = AppointmentStatus.CANCELLED
                    self.db.commit()
                    self.db.refresh(appointment)
                    return f"Your appointment with Dr. {doctor_user.first_name} {doctor_user.last_name} on {appointment.start_time.strftime('%Y-%m-%d %I:%M %p')} has been cancelled."
            # --- NATURAL LANGUAGE RESCHEDULE (IMPROVED AMBIGUITY HANDLING & FLEXIBILITY) ---
            resched_match = re.search(r"reschedul(?:e|ing|ed|ule|uled|uling|ul|ule)? (?:my )?appointment(?: with dr\.?\s*([A-Za-z]+)(?:\s+([A-Za-z]+))?)?(?: for| to| on| at)? ([^\n]+)", msg, re.IGNORECASE)
            if resched_match:
                doctor_first = resched_match.group(1)
                doctor_last = resched_match.group(2) if resched_match.group(2) else None
                date_time_str = resched_match.group(3)
                # Find doctor user (optional)
                doctor_user = None
                doctor_profile = None
                if doctor_first:
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
                    if not doctor_user:
                        return "Sorry, I could not find the specified doctor. Please check the doctor's name."
                    doctor_profile = self.db.query(Doctor).filter_by(user_id=doctor_user.id).first()
                    if not doctor_profile:
                        return "Sorry, I could not find the doctor's profile."
                # Find user's appointments (optionally with doctor)
                query = self.db.query(Appointment).filter(
                    Appointment.user_id == user_id,
                    Appointment.status.in_([AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED])
                )
                if doctor_profile:
                    query = query.filter(Appointment.doctor_id == doctor_profile.id)
                matches = query.order_by(Appointment.start_time.asc()).all()
                if not matches:
                    return "No upcoming appointment found to reschedule." if not doctor_profile else f"No upcoming appointment found with Dr. {doctor_user.last_name}."
                if len(matches) > 1:
                    lines = []
                    for apt in matches:
                        doctor_name = f"Dr. {apt.doctor.user.first_name} {apt.doctor.user.last_name}" if apt.doctor and apt.doctor.user else "(Unknown Doctor)"
                        lines.append(f"ID: {apt.id} | {apt.start_time.strftime('%Y-%m-%d %I:%M %p')} with {doctor_name} | Status: {apt.status.value}")
                    return "Multiple appointments found. Please specify the appointment ID to reschedule:\n" + "\n".join(lines)
                appointment = matches[0]
                # Parse new date and time
                try:
                    new_start = date_parser.parse(date_time_str, fuzzy=True, dayfirst=True)
                except Exception:
                    return "Sorry, I could not understand the new date and time. Please specify clearly."
                # If only time is given, use the original date
                if new_start.year == 1900:
                    new_start = appointment.start_time.replace(hour=new_start.hour, minute=new_start.minute, second=0, microsecond=0)
                # Set end time (30 min duration)
                new_end = new_start + timedelta(minutes=30)
                # Check for conflicts
                overlapping = self.db.query(Appointment).filter(
                    Appointment.doctor_id == appointment.doctor_id,
                    Appointment.id != appointment.id,
                    Appointment.start_time < new_end,
                    Appointment.end_time > new_start
                ).first()
                if overlapping:
                    return "Sorry, the doctor is not available at that time. Please choose another slot."
                # Update appointment
                appointment.start_time = new_start
                appointment.end_time = new_end
                self.db.commit()
                self.db.refresh(appointment)
                return f"Your appointment has been rescheduled to {new_start.strftime('%Y-%m-%d %I:%M %p')}."
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
            doctor_match = re.search(r"Dr\.?\s*([A-Za-z]+)(?:\s+([A-Za-z]+))?", message)
            # Flexible date extraction: look for 'on <date>' or any date-like string
            date_match = re.search(r"on ([^,]+)", message, re.IGNORECASE)
            if not date_match:
                date_match = re.search(r"today|tomorrow|\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{2,4}|\d{1,2}(?:st|nd|rd|th)? [A-Za-z]+ \d{4}", message, re.IGNORECASE)
            time_match = re.search(r"(\d{1,2})(?::(\d{2}))?\s*(a\.m\.|am|p\.m\.|pm)?", message, re.IGNORECASE)
            # Extract reason (improved: stop at doctor/time/date keywords)
            reason_match = re.search(
                r"for (.+?)(?= with dr| with doctor| tomorrow| today| at | on | by | for | in | from | am| pm| a\.m\.| p\.m\.|$)",
                message,
                re.IGNORECASE
            )
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
                # Parse date using dateutil for flexibility
                date_str = None
                if date_match.group(0).lower() == "tomorrow":
                    start_date = datetime.now() + timedelta(days=1)
                elif date_match.group(0).lower() == "today":
                    start_date = datetime.now()
                else:
                    try:
                        # Try to parse the date string flexibly
                        date_str = date_match.group(1) if date_match.lastindex else date_match.group(0)
                        start_date = date_parser.parse(date_str, fuzzy=True, dayfirst=True)
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
