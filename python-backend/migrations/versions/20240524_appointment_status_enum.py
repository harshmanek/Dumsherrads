"""
Revision ID: 20240524_appointment_status_enum
Revises: 
Create Date: 2025-05-24

This migration alters the 'status' column in the 'appointments' table to allow the full enum values (PENDING, CONFIRMED, CANCELLED, COMPLETED).
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20240524_appointment_status_enum'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.execute("ALTER TABLE appointments MODIFY COLUMN status ENUM('PENDING', 'CONFIRMED', 'CANCELLED', 'COMPLETED') NOT NULL;")

def downgrade():
    op.execute("ALTER TABLE appointments MODIFY COLUMN status VARCHAR(1) NOT NULL;")

