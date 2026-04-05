"""bookings module: lesson recurrence, monitor availability, booking, stable config

Revision ID: d1e2f3a4b5c6
Revises: c1d2e3f4a5b6
Create Date: 2026-04-05 14:00:00.000000
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "d1e2f3a4b5c6"
down_revision: Union[str, Sequence[str], None] = "c1d2e3f4a5b6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Tabla lessonrecurrence
    op.create_table(
        "lessonrecurrence",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("stable_id", sa.Integer(), nullable=False),
        sa.Column("instructor_id", sa.Integer(), nullable=False),
        sa.Column("helper_id", sa.Integer(), nullable=True),
        sa.Column("track_id", sa.Integer(), nullable=True),
        sa.Column("day_of_week", sa.Integer(), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=True),
        sa.Column("from_date", sa.Date(), nullable=False),
        sa.Column("to_date", sa.Date(), nullable=False),
        sa.Column("max_students", sa.Integer(), nullable=True),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["helper_id"], ["user.id"]),
        sa.ForeignKeyConstraint(["instructor_id"], ["user.id"]),
        sa.ForeignKeyConstraint(["stable_id"], ["stable.id"]),
        sa.ForeignKeyConstraint(["track_id"], ["track.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_lessonrecurrence_stable_id", "lessonrecurrence", ["stable_id"])

    # 2. Añadir columnas a lesson
    op.add_column("lesson", sa.Column("max_students", sa.Integer(), nullable=True))
    op.add_column("lesson", sa.Column("is_published", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("lesson", sa.Column("recurrence_id", sa.Integer(), nullable=True))
    op.create_foreign_key("fk_lesson_recurrence_id", "lesson", "lessonrecurrence", ["recurrence_id"], ["id"])

    # 3. Tabla monitoravailability
    op.create_table(
        "monitoravailability",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("stable_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("is_recurring", sa.Boolean(), nullable=False),
        sa.Column("day_of_week", sa.Integer(), nullable=True),
        sa.Column("specific_date", sa.Date(), nullable=True),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["stable_id"], ["stable.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_monitoravailability_stable_id", "monitoravailability", ["stable_id"])

    # 4. Enum y tabla booking
    bookingstatus = sa.Enum("RESERVADO", "CANCELADO", "ASISTIO", "NO_ASISTIO", name="bookingstatus")
    bookingstatus.create(op.get_bind())

    op.create_table(
        "booking",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("stable_id", sa.Integer(), nullable=False),
        sa.Column("lesson_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.Enum("RESERVADO", "CANCELADO", "ASISTIO", "NO_ASISTIO", name="bookingstatus"), nullable=False),
        sa.Column("horse_request", sa.String(), nullable=True),
        sa.Column("notes", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("cancelled_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["lesson_id"], ["lesson.id"]),
        sa.ForeignKeyConstraint(["stable_id"], ["stable.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("lesson_id", "user_id", name="uq_booking_lesson_user"),
    )
    op.create_index("ix_booking_stable_id", "booking", ["stable_id"])

    # 5. Tabla stableconfig
    op.create_table(
        "stableconfig",
        sa.Column("stable_id", sa.Integer(), nullable=False),
        sa.Column("cancel_deadline_hours", sa.Integer(), nullable=False, server_default="24"),
        sa.Column("auto_attendance", sa.Boolean(), nullable=False, server_default="false"),
        sa.ForeignKeyConstraint(["stable_id"], ["stable.id"]),
        sa.PrimaryKeyConstraint("stable_id"),
    )


def downgrade() -> None:
    op.drop_table("stableconfig")
    op.drop_index("ix_booking_stable_id", table_name="booking")
    op.drop_table("booking")
    op.execute("DROP TYPE bookingstatus")
    op.drop_index("ix_monitoravailability_stable_id", table_name="monitoravailability")
    op.drop_table("monitoravailability")
    op.drop_constraint("fk_lesson_recurrence_id", "lesson", type_="foreignkey")
    op.drop_column("lesson", "recurrence_id")
    op.drop_column("lesson", "is_published")
    op.drop_column("lesson", "max_students")
    op.drop_index("ix_lessonrecurrence_stable_id", table_name="lessonrecurrence")
    op.drop_table("lessonrecurrence")
