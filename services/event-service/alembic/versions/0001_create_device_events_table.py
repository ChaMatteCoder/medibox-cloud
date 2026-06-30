"""create device events table

Revision ID: event_0001
Revises:
Create Date: 2026-06-30
"""

from alembic import op
import sqlalchemy as sa

revision = "event_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "device_events",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("patient_id", sa.String(length=36), nullable=False),
        sa.Column("medication_id", sa.String(length=36), nullable=False),
        sa.Column("event_type", sa.String(length=40), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_device_events_patient_id", "device_events", ["patient_id"])
    op.create_index("ix_device_events_event_type", "device_events", ["event_type"])


def downgrade() -> None:
    op.drop_index("ix_device_events_event_type", table_name="device_events")
    op.drop_index("ix_device_events_patient_id", table_name="device_events")
    op.drop_table("device_events")
