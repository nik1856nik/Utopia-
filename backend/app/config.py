import os
from sqlalchemy.engine import URL, make_url

_database_url = os.getenv("DATABASE_URL", "").strip()
if _database_url:
    if make_url(_database_url).drivername != "postgresql+psycopg":
        raise RuntimeError("Only PostgreSQL is supported. Set DATABASE_URL to a postgresql+psycopg:// URL.")
    DB_URL = _database_url
else:
    _database_password = os.getenv("DATABASE_PASSWORD")
    if not _database_password:
        raise RuntimeError("Set DATABASE_URL or DATABASE_PASSWORD and PostgreSQL connection settings.")
    DB_URL = URL.create(
        "postgresql+psycopg",
        username=os.getenv("DATABASE_USER", "civicgrid"),
        password=_database_password,
        host=os.getenv("DATABASE_HOST", "localhost"),
        port=int(os.getenv("DATABASE_PORT", "5432")),
        database=os.getenv("DATABASE_NAME", "civicgrid"),
    )
NOMINATIM_BASE_URL = os.getenv("NOMINATIM_BASE_URL", "https://nominatim.openstreetmap.org").rstrip("/")
NOMINATIM_USER_AGENT = os.getenv("NOMINATIM_USER_AGENT", "UtopiaMunicipalPlatform/3.0")
JWT_SECRET = os.getenv("JWT_SECRET", "").strip()
if len(JWT_SECRET) < 32:
    raise RuntimeError("JWT_SECRET is required and must be at least 32 characters; generate one with openssl rand -hex 48.")
JWT_ALGORITHM = "HS256"

# Demo authorized municipal officers with Employee IDs (Badge IDs) and supported aliases
MUNICIPAL_USERS = {
    "admin@gcc.gov.in": {
        "password": "admin123",
        "name": "Er. S. Radhakrishnan",
        "role": "admin",
        "department": "Greater Chennai Corporation",
        "designation": "Superintending Engineer (Works)",
        "badge_id": "GCC-ENG-0842",
        "aliases": ["GCC-ENG-0842", "admin@gcc.gov.in", "admin", "gcc-admin"]
    },
    "water@metrowater.tn.gov.in": {
        "password": "water123",
        "name": "Dr. V. Meenakshi",
        "role": "official",
        "department": "Chennai Metro Water",
        "designation": "Executive Engineer (Pipelines)",
        "badge_id": "CMW-DIV-0219",
        "aliases": ["CMW-DIV-0219", "water@metrowater.tn.gov.in", "water"]
    },
    "roads@gcc.gov.in": {
        "password": "roads123",
        "name": "Er. K. Ramanathan",
        "role": "official",
        "department": "GCC Roads & Bridges",
        "designation": "Divisional Engineer (Zone 10)",
        "badge_id": "GCC-RD-0155",
        "aliases": ["GCC-RD-0155", "roads@gcc.gov.in", "roads"]
    },
    "power@tangedco.gov.in": {
        "password": "power123",
        "name": "Er. Anitha Selvan",
        "role": "official",
        "department": "TANGEDCO",
        "designation": "Assistant Executive Engineer (O&M)",
        "badge_id": "TNEB-ZN-3310",
        "aliases": ["TNEB-ZN-3310", "TNEB-AEE-4091", "power@tangedco.gov.in", "power", "tangedco"]
    },
    "drainage@gcc.gov.in": {
        "password": "drain123",
        "name": "Er. M. Gunasekaran",
        "role": "official",
        "department": "Stormwater Drainage",
        "designation": "Executive Engineer (SWD)",
        "badge_id": "SWD-ZN-0418",
        "aliases": ["SWD-ZN-0418", "SWD-ENG-1102", "drainage@gcc.gov.in", "swd@gcc.gov.in", "drainage", "stormwater"]
    },
    "field.gcc@chennai.gov.in": {
        "password": "field123",
        "name": "M. Selvam",
        "role": "onsite",
        "department": "GCC Roads & Bridges",
        "designation": "Field Supervisor (Zone 10)",
        "badge_id": "GCC-FIELD-552",
        "aliases": ["GCC-FIELD-552", "field.gcc@chennai.gov.in"]
    },
    "field.water@metrowater.tn.gov.in": {
        "password": "field123",
        "name": "R. Prakash",
        "role": "onsite",
        "department": "Chennai Metro Water",
        "designation": "Site Trenching Foreman",
        "badge_id": "CMW-SITE-884",
        "aliases": ["CMW-SITE-884", "field.water@metrowater.tn.gov.in"]
    },
    "field.power@tangedco.gov.in": {
        "password": "field123",
        "name": "S. Kumar",
        "role": "onsite",
        "department": "TANGEDCO",
        "designation": "Field Line & Cable Engineer",
        "badge_id": "TNEB-SITE-312",
        "aliases": ["TNEB-SITE-312", "field.power@tangedco.gov.in"]
    }
}
