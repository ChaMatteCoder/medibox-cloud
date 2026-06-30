"""create medication tables

Revision ID: medication_0001
Revises:
Create Date: 2026-06-30
"""

from alembic import op
import sqlalchemy as sa

revision = "medication_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "patients",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("birth_date", sa.Date(), nullable=False),
        sa.Column("caregiver_id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_patients_caregiver_id", "patients", ["caregiver_id"])

    op.create_table(
        "medications",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("patient_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("dosage", sa.String(length=120), nullable=False),
        sa.Column("instructions", sa.Text(), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["patient_id"], ["patients.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_medications_patient_id", "medications", ["patient_id"])

    op.create_table(
        "medication_schedules",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("medication_id", sa.String(length=36), nullable=False),
        sa.Column("scheduled_time", sa.Time(), nullable=False),
        sa.Column("weekdays", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["medication_id"], ["medications.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_medication_schedules_medication_id",
        "medication_schedules",
        ["medication_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_medication_schedules_medication_id", table_name="medication_schedules")
    op.drop_table("medication_schedules")
    op.drop_index("ix_medications_patient_id", table_name="medications")
    op.drop_table("medications")
    op.drop_index("ix_patients_caregiver_id", table_name="patients")
    op.drop_table("patients")
