from sqlalchemy import text
from . import engine, SessionLocal
from ..models import Base
import logging
import traceback

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    """Initialize the database by dropping and recreating all tables"""
    try:
        # Get a database connection
        with engine.connect() as connection:
            # # Drop all tables
            # logger.info("Dropping all tables...")
            # Base.metadata.drop_all(bind=engine)
            # logger.info("All tables dropped successfully")

            # Create all tables
            logger.info("Creating all tables(if not exists)...")
            Base.metadata.create_all(bind=engine)
            logger.info("All tables created successfully(if not exists)")

            # Create initial data
            # create_initial_data(connection)

    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        logger.error(traceback.format_exc())
        raise

def create_initial_data(connection):
    """Create initial data in the database"""
    try:
        # Create admin user
        admin_query = text("""
            INSERT INTO users (id, email, password, first_name, last_name, role, is_active)
            VALUES (1, 'admin@example.com', 'admin123', 'Admin', 'User', 'ADMIN', true)
        """)
        connection.execute(admin_query)

        # Create a test doctor
        doctor_query = text("""
            INSERT INTO users (id, email, password, first_name, last_name, role, is_active)
            VALUES (2, 'doctor@example.com', 'doctor123', 'John', 'Smith', 'DOCTOR', true)
        """)
        connection.execute(doctor_query)

        # Create doctor profile
        doctor_profile_query = text("""
            INSERT INTO doctors (id, user_id, specialization, license_number)
            VALUES (1, 2, 'General Medicine', 'MD123456')
        """)
        connection.execute(doctor_profile_query)

        # Create a test patient
        patient_query = text("""
            INSERT INTO users (id, email, password, first_name, last_name, role, is_active)
            VALUES (3, 'patient@example.com', 'patient123', 'Jane', 'Doe', 'PATIENT', true)
        """)
        connection.execute(patient_query)

        connection.commit()
        logger.info("Initial data created successfully")

    except Exception as e:
        logger.error(f"Error creating initial data: {str(e)}")
        logger.error(traceback.format_exc())
        raise

if __name__ == "__main__":
    logger.info("Creating initial data")
    init_db()
    logger.info("Initial data creation finished") 