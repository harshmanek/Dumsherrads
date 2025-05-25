# VOICEBOT AI ASSISTANT

> AI That Speaks Health \
>“An AI voice assistant that books hospital appointments — faster, smarter, human-free.”

# Project Name
Hospital Appointment Management System with AI Voice Assistant

# Tagline
Effortlessly manage hospital appointments with a smart, voice-enabled AI assistant.

---

## 1. Problem It Solves
Managing medical appointments can be time-consuming and confusing for patients and hospital staff. Manual scheduling, rescheduling, and tracking often lead to errors, missed appointments, and poor patient experience. This project provides an intelligent, user-friendly platform for patients to book, manage, and interact with their appointments using both text and voice, reducing administrative burden and improving healthcare accessibility.

---

## 2. Challenge You Ran Into
**Challenge:** Integrating real-time voice transcription and natural language understanding with secure, role-based appointment management.

**Solution:** Leveraged OpenAI Whisper for robust voice-to-text transcription, FastAPI for secure backend APIs with JWT authentication, and React for a responsive frontend. Overcame CORS, audio processing, and authentication hurdles by modularizing the codebase, using context providers, and thorough error handling.

---

## 3. Technologies You Used
- **Frontend:**
  - React (v18.2.0)
  - React Router DOM (v6.20.0)
  - Axios (v1.6.2)
  - Vite (v5.0.0)
  - React Speech Recognition (v3.10.0)
- **Backend:**
  - FastAPI (v0.109.2)
  - Uvicorn (v0.27.1)
  - SQLAlchemy (v2.0.27)
  - PyMySQL (v1.1.0)
  - Pydantic (v2.6.1)
  - OpenAI Whisper (latest)
  - LangChain (v0.1.9)
  - Python-Jose, Passlib, Bcrypt (for auth)
- **Database:**
  - MySQL (or compatible)
- **Other:**
  - Python-dotenv

---

## 4. Platform
**Web** (cross-platform: Windows, Linux, MacOS)

---

## 5. Project Overview & Architecture
A fullstack web application for hospital appointment management, featuring:
- Secure user authentication (JWT)
- Role-based access (Patient, Doctor, Admin)
- Appointment scheduling, updating, and cancellation
- Doctor management
- AI-powered chatbot with voice and text input
- RESTful API backend

**Architecture Diagram (Text):**
```
[Frontend (React)] <----> [FastAPI Backend] <----> [MySQL DB]
         |                        |
   [Voice Input]           [OpenAI Whisper]
         |                        |
   [Chatbot UI]         [LangChain Agent]
```

---

## 6. Backend API Documentation
### Authentication
- **POST /auth/login**
  - Request: `{ email, password }`
  - Response: `{ access_token, token_type }`
- **POST /auth/register**
  - Request: `{ email, password, first_name, last_name, role }`
  - Response: `{ access_token, token_type }`
- **GET /auth/me**
  - Returns current user info (JWT required)

### Users
- **GET /users/** — List all users (admin only)
- **GET /users/{user_id}** — Get user by ID
- **POST /users/** — Create user
- **PUT /users/{user_id}** — Update user
- **DELETE /users/{user_id}** — Delete user

### Appointments
- **GET /appointments/** — List your appointments
- **GET /appointments/{id}** — Get appointment details
- **POST /appointments/** — Create appointment
- **PUT /appointments/{id}** — Update appointment
- **DELETE /appointments/{id}** — Delete appointment

### Doctors
- **GET /doctors/** — List all doctors
- **GET /doctors/{id}** — Get doctor details
- **POST /doctors/** — Create doctor profile
- **PUT /doctors/{id}** — Update doctor profile
- **DELETE /doctors/{id}** — Delete doctor profile

### Agent (AI Chatbot)
- **POST /agent/chat**
  - Request: `{ message }` (JWT required)
  - Response: `{ response }`

### Voice (Whisper)
- **POST /whisper/transcribe**
  - Request: `file` (audio/wav)
  - Response: `{ transcription }`
- **POST /whisper/voice-agent**
  - Request: `file` (audio/wav)
  - Response: `{ transcription, agent_reply }`

---

## 7. Frontend Usage
- **Login/Register:** Secure authentication for patients and doctors.
- **Dashboard:** View, book, reschedule, or cancel appointments.
- **Chatbot:**
  - Type or speak your requests (e.g., "Book an appointment with Dr. Smith on Friday at 3pm").
  - The bot responds with confirmations, summaries, and can handle rescheduling/cancellations.
- **Doctor Management:** (for admin/doctor roles)
- **Responsive UI:** Works on desktop and mobile browsers.

---

## 8. Setup & Installation
### Backend
```bash
cd python-backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
# Set up .env file with DB and secret config
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## 9. Usage Instructions
- Register or log in.
- Use the dashboard or chatbot to manage appointments.
- Use the microphone button to speak your requests.
- Doctors can view/manage their appointments and profiles.

---

## 10. How to Extend/Contribute
- Fork the repo, create a branch, and submit a PR.
- Add new features (e.g., notifications, calendar sync, admin analytics).
- Improve AI agent with more medical logic or integrations.

---

## 11. Links
- **GitHub Repository:** [https://github.com/harshmanek/Dumsherrads]
- **PPT:** [Add your link here]
- **Video Demo:** [Add your YouTube link here]

---

## 12. Images & Logo
- **Cover Image:** [Add your image here]
- **Screenshots:** [Add your images here]
- **Logo:** [VOICEBOT_Logo.png]

---

## 13. Contact & Credits
- Built by [DumSherrads/Riddhi Ladva/ Harsh Manek]
- For Holboxathon 2024

---

**Thank you for reviewing our project!** 