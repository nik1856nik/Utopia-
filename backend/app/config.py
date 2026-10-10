import os

DB_URL = os.getenv('DATABASE_URL', 'sqlite:///./civicgrid.db')
JWT_SECRET = os.getenv("JWT_SECRET", "utopia-super-secret-key-2026")
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
