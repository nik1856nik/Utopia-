from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from .config import DB_URL

engine = create_engine(
    DB_URL,
    connect_args={'check_same_thread': False} if DB_URL.startswith('sqlite') else {}
)
SessionLocal = sessionmaker(bind=engine, autoflush=False)

class Base(DeclarativeBase):
    pass

def get_db():
    s = SessionLocal()
    try:
        yield s
    finally:
        s.close()

# Alias for backwards compatibility
db = get_db

def ensure_columns(target_engine):
    """Ensure newly added columns exist in older SQLite or Postgres databases without breaking."""
    with target_engine.connect() as conn:
        for col, col_type in [
            ('current_step', 'INTEGER DEFAULT 3'),
            ('contact_engineer_name', "VARCHAR(120) DEFAULT 'Er. K. Ramanathan'"),
            ('contact_engineer_phone', "VARCHAR(40) DEFAULT '+91 94440 28192'"),
            ('contact_engineer_email', "VARCHAR(100) DEFAULT 'engineer.civicworks@chennaicorporation.gov.in'"),
            ('contact_contractor', "VARCHAR(120) DEFAULT 'MetroLink Infrastructure Ltd.'"),
            ('contact_contractor_phone', "VARCHAR(40) DEFAULT '+91 98841 55210'"),
            ('noise_warning', "VARCHAR(200) DEFAULT 'Permitted high-noise window: 22:00 - 04:00'"),
            ('dust_warning', "VARCHAR(200) DEFAULT 'Trenching dust window: 09:00 - 14:00'"),
            ('gmaps_broadcast', "BOOLEAN DEFAULT 1"),
            ('detour_advice', "VARCHAR(200) DEFAULT 'Traffic diversion via Panagal Park'"),
            ('technical_scope', "TEXT"),
            ('funding_program', "VARCHAR(120) DEFAULT 'Municipal Infrastructure Capital Fund'"),
            ('created_by', "VARCHAR(120) DEFAULT 'Official Sanction'")
        ]:
            try:
                conn.execute(text(f"ALTER TABLE projects ADD COLUMN {col} {col_type}"))
                conn.commit()
            except Exception:
                pass

        for col, col_type in [
            ('department', "VARCHAR(100) DEFAULT 'Greater Chennai Corporation'"),
            ('phone', 'VARCHAR(20)'),
            ('email', 'VARCHAR(100)'),
            ('pincode', 'VARCHAR(6)'),
            ('is_question', 'BOOLEAN DEFAULT 0'),
            ('intimated_in_advance', 'BOOLEAN DEFAULT 0'),
            ('official_reply', 'TEXT'),
            ('replied_at', 'TIMESTAMP'),
            ('replied_by', 'VARCHAR(120)')
        ]:
            try:
                conn.execute(text(f"ALTER TABLE issues ADD COLUMN {col} {col_type}"))
                conn.commit()
            except Exception:
                pass

        for col, col_type in [
            ('requesting_dept_notified', 'BOOLEAN DEFAULT 0'),
            ('conflicting_dept_notified', 'BOOLEAN DEFAULT 0'),
            ('approved_dept', 'VARCHAR(100)'),
            ('rescheduled_dept', 'VARCHAR(100)'),
            ('rescheduled_start', 'DATE'),
            ('rescheduled_end', 'DATE'),
            ('rescheduled_status', 'VARCHAR(50)'),
            ('requesting_project_id', 'INTEGER'),
            ('proposed_category', 'VARCHAR(100)'),
            ('proposed_description', 'TEXT'),
            ('proposed_budget', 'INTEGER'),
            ('ward_id', 'INTEGER'),
            ('lat', 'FLOAT'),
            ('lng', 'FLOAT'),
        ]:
            try:
                conn.execute(text(f"ALTER TABLE conflict_tickets ADD COLUMN {col} {col_type}"))
                conn.commit()
            except Exception:
                pass
