from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from .config import DB_URL

engine = create_engine(DB_URL, pool_pre_ping=True)
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
    """Add missing legacy columns without issuing duplicate DDL on PostgreSQL."""
    column_specs = {
        'projects': [
            ('current_step', 'INTEGER DEFAULT 3'),
            ('contact_engineer_name', "VARCHAR(120) DEFAULT 'Er. K. Ramanathan'"),
            ('contact_engineer_phone', "VARCHAR(40) DEFAULT '+91 94440 28192'"),
            ('contact_engineer_email', "VARCHAR(100) DEFAULT 'engineer.civicworks@chennaicorporation.gov.in'"),
            ('contact_contractor', "VARCHAR(120) DEFAULT 'MetroLink Infrastructure Ltd.'"),
            ('contact_contractor_phone', "VARCHAR(40) DEFAULT '+91 98841 55210'"),
            ('noise_warning', "VARCHAR(200) DEFAULT 'Permitted high-noise window: 22:00 - 04:00'"),
            ('dust_warning', "VARCHAR(200) DEFAULT 'Trenching dust window: 09:00 - 14:00'"),
            ('gmaps_broadcast', "BOOLEAN DEFAULT TRUE"),
            ('detour_advice', "VARCHAR(200) DEFAULT 'Traffic diversion via Panagal Park'"),
            ('technical_scope', "TEXT"),
            ('funding_program', "VARCHAR(120) DEFAULT 'Municipal Infrastructure Capital Fund'"),
            ('created_by', "VARCHAR(120) DEFAULT 'Official Sanction'")
        ],
        'issues': [
            ('department', "VARCHAR(100) DEFAULT 'Greater Chennai Corporation'"),
            ('phone', 'VARCHAR(20)'),
            ('email', 'VARCHAR(100)'),
            ('pincode', 'VARCHAR(6)'),
            ('is_question', 'BOOLEAN DEFAULT FALSE'),
            ('intimated_in_advance', 'BOOLEAN DEFAULT FALSE'),
            ('official_reply', 'TEXT'),
            ('replied_at', 'TIMESTAMP'),
            ('replied_by', 'VARCHAR(120)')
        ],
        'conflict_tickets': [
            ('requesting_dept_notified', 'BOOLEAN DEFAULT FALSE'),
            ('conflicting_dept_notified', 'BOOLEAN DEFAULT FALSE'),
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
        ],
    }

    for table, columns in column_specs.items():
        existing_tables = inspect(target_engine).get_table_names()
        if table not in existing_tables:
            continue
        existing_columns = {column['name'] for column in inspect(target_engine).get_columns(table)}
        for col, col_type in columns:
            if col in existing_columns:
                continue
            with target_engine.begin() as conn:
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}"))
            existing_columns.add(col)

    # Widen old PostgreSQL installs to match Issue.kind before seeding or writes.
    if 'issues' in inspect(target_engine).get_table_names():
        kind = next((column for column in inspect(target_engine).get_columns('issues') if column['name'] == 'kind'), None)
        if kind and getattr(kind['type'], 'length', None) is not None and kind['type'].length < 180:
            with target_engine.begin() as conn:
                conn.execute(text('ALTER TABLE issues ALTER COLUMN kind TYPE VARCHAR(180)'))
