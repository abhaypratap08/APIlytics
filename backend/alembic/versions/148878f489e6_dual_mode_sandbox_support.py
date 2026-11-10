"""dual_mode_sandbox_support

Adds sandbox_sessions, and extends telemetry_events with source attribution 
fields (sandbox_session_id, source_type, origin_host, resource_type, failure_kind).
Makes integration_id and status_code nullable to support browser network failures.

Revision ID: 148878f489e6
Revises: ec4e404d0404
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "148878f489e6"
down_revision = "ec4e404d0404"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Create SandboxSession table
    op.create_table(
        "sandbox_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("status", sa.String(32), nullable=False, server_default="active"),
        sa.Column("target_url", sa.String(2048), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    # 2. Add new columns to telemetry_events (Nullable initially so we don't break existing rows)
    op.add_column("telemetry_events", sa.Column("source_type", sa.String(32), nullable=True))
    op.add_column("telemetry_events", sa.Column("sandbox_session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("sandbox_sessions.id", ondelete="CASCADE"), nullable=True, index=True))
    op.add_column("telemetry_events", sa.Column("origin_host", sa.String(255), nullable=True))
    op.add_column("telemetry_events", sa.Column("resource_type", sa.String(32), nullable=True))
    op.add_column("telemetry_events", sa.Column("failure_kind", sa.String(64), nullable=True))

    # 3. Alter existing columns to allow NULLs
    op.alter_column("telemetry_events", "integration_id", existing_type=postgresql.UUID(as_uuid=True), nullable=True)
    op.alter_column("telemetry_events", "status_code", existing_type=sa.Integer(), nullable=True)

    # 4. Backfill source_type for existing NGINX data
    op.execute("UPDATE telemetry_events SET source_type = 'nginx' WHERE integration_id IS NOT NULL")
    
    # 5. Make source_type NOT NULL after backfill
    op.alter_column("telemetry_events", "source_type", existing_type=sa.String(32), nullable=False)

    # 6. Add Check Constraint
    op.create_check_constraint(
        "ck_telemetry_source_attribution",
        "telemetry_events",
        "(integration_id IS NOT NULL AND sandbox_session_id IS NULL) OR "
        "(integration_id IS NULL AND sandbox_session_id IS NOT NULL)"
    )


def downgrade() -> None:
    op.drop_constraint("ck_telemetry_source_attribution", "telemetry_events", type_="check")
    
    op.alter_column("telemetry_events", "status_code", existing_type=sa.Integer(), nullable=False)
    op.alter_column("telemetry_events", "integration_id", existing_type=postgresql.UUID(as_uuid=True), nullable=False)
    
    op.drop_column("telemetry_events", "source_type")
    op.drop_column("telemetry_events", "sandbox_session_id")
    op.drop_column("telemetry_events", "origin_host")
    op.drop_column("telemetry_events", "resource_type")
    op.drop_column("telemetry_events", "failure_kind")

    op.drop_table("sandbox_sessions")
