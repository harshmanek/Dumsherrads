import requests
import json
from datetime import datetime, timedelta
import sys
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"

def wait_for_server(max_retries=5, delay=2):
    """Wait for the server to be ready"""
    for i in range(max_retries):
        try:
            logger.info(f"Attempting to connect to server (attempt {i + 1}/{max_retries})...")
            response = requests.get(f"{BASE_URL}/docs")
            if response.status_code == 200:
                logger.info("Server is ready!")
                return True
        except requests.exceptions.ConnectionError as e:
            logger.warning(f"Connection failed: {str(e)}")
            if i < max_retries - 1:
                logger.info(f"Waiting {delay} seconds before next attempt...")
                time.sleep(delay)
            else:
                logger.error("Could not connect to the server. Make sure it's running with 'uvicorn app.main:app --reload'")
                return False
    return False

def test_agent_chat():
    """Test the appointment agent chat endpoint"""
    try:
        url = f"{BASE_URL}/agent/chat"
        data = {
            "message": "I need to schedule an appointment with Dr. Smith for tomorrow afternoon",
            "user_id": 3
        }
        logger.info("Testing agent chat endpoint...")
        response = requests.post(url, json=data)
        logger.info(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            logger.info(f"Response: {response.json()}")
        else:
            logger.error(f"Error: {response.text}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error testing agent chat: {str(e)}")

def test_create_appointment():
    """Test creating a new appointment"""
    try:
        url = f"{BASE_URL}/appointments"
        tomorrow = datetime.now() + timedelta(days=1)
        data = {
            "user_id": 3,
            "doctor_id": 1,
            "start_time": tomorrow.replace(hour=14, minute=0).isoformat(),
            "end_time": tomorrow.replace(hour=14, minute=30).isoformat(),
            "reason": "Regular checkup",
            "status": "PENDING"
        }
        logger.info("Testing create appointment endpoint...")
        response = requests.post(url, json=data)
        logger.info(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            logger.info(f"Response: {response.json()}")
            return response.json().get("id")
        else:
            logger.error(f"Error: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error creating appointment: {str(e)}")
        return None

def test_get_appointment(appointment_id):
    """Test getting an appointment"""
    try:
        url = f"{BASE_URL}/appointments/{appointment_id}"
        logger.info(f"Testing get appointment endpoint for ID: {appointment_id}...")
        response = requests.get(url)
        logger.info(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            logger.info(f"Response: {response.json()}")
        else:
            logger.error(f"Error: {response.text}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error getting appointment: {str(e)}")

def test_update_appointment(appointment_id):
    """Test updating an appointment"""
    try:
        url = f"{BASE_URL}/appointments/{appointment_id}"
        data = {
            "reason": "Updated: Urgent checkup",
            "status": "CONFIRMED"
        }
        logger.info(f"Testing update appointment endpoint for ID: {appointment_id}...")
        response = requests.put(url, json=data)
        logger.info(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            logger.info(f"Response: {response.json()}")
        else:
            logger.error(f"Error: {response.text}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error updating appointment: {str(e)}")

def test_delete_appointment(appointment_id):
    """Test deleting an appointment"""
    try:
        url = f"{BASE_URL}/appointments/{appointment_id}"
        logger.info(f"Testing delete appointment endpoint for ID: {appointment_id}...")
        response = requests.delete(url)
        logger.info(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            logger.info(f"Response: {response.json()}")
        else:
            logger.error(f"Error: {response.text}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error deleting appointment: {str(e)}")

def run_all_tests():
    """Run all test cases"""
    logger.info("Starting API Tests...")
    
    # Wait for server to be ready
    if not wait_for_server():
        sys.exit(1)
    
    # Test agent chat
    test_agent_chat()
    
    # Test appointment CRUD operations
    appointment_id = test_create_appointment()
    if appointment_id:
        test_get_appointment(appointment_id)
        test_update_appointment(appointment_id)
        test_delete_appointment(appointment_id)

if __name__ == "__main__":
    run_all_tests() 