"""mode_b_foundation

Adds projects and integrations. Re-creates telemetry_events with
project_id/integration_id foreign keys.

telemetry_events is dropped and recreated because the MVP has no
real customer data yet. Once real data exists, future migrations
must be additive with backfills.

Revision ID: ec4e404d0404
Revises: 3a68abde6cf9
Create Date: 2026-11-10
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "ec4e404d0404"
down_revision = "3a68abde6cf9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "projects",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(32), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    op.create_table(
        "integrations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("projects.id", ondelete="CASCADE"),
                  nullable=False, index=True),
        sa.Column("provider", sa.String(64), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("credential_hash", sa.String(64), unique=True, nullable=False, index=True),
        sa.Column("status", sa.String(32), nullable=False, server_default="active"),
        sa.Column("last_event_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    op.drop_table("telemetry_events")

    op.create_table(
        "telemetry_events",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("event_id", postgresql.UUID(as_uuid=True), unique=True, nullable=False, index=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("projects.id", ondelete="CASCADE"),
                  nullable=False, index=True),
        sa.Column("integration_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("integrations.id", ondelete="CASCADE"),
                  nullable=False, index=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column("method", sa.String(10), nullable=False),
        sa.Column("route_template", sa.String(512), nullable=False, index=True),
        sa.Column("status_code", sa.Integer(), nullable=False, index=True),
        sa.Column("latency_ms", sa.Double(), nullable=False),
        sa.Column("request_size_bytes", sa.Integer(), nullable=True),
        sa.Column("response_size_bytes", sa.Integer(), nullable=True),
        sa.Column("client_id", sa.String(128), nullable=True, index=True),
        sa.Column("service_name", sa.String(128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("telemetry_events")
    op.drop_table("integrations")
    op.drop_table("projects")

    op.create_table(
        "telemetry_events",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("event_id", postgresql.UUID(as_uuid=True), unique=True, nullable=False, index=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column("method", sa.String(10), nullable=False),
        sa.Column("route_template", sa.String(512), nullable=False, index=True),
        sa.Column("status_code", sa.Integer(), nullable=False, index=True),
        sa.Column("latency_ms", sa.Double(), nullable=False),
        sa.Column("request_size_bytes", sa.Integer(), nullable=True),
        sa.Column("response_size_bytes", sa.Integer(), nullable=True),
        sa.Column("client_id", sa.String(128), nullable=True, index=True),
        sa.Column("service_name", sa.String(128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
