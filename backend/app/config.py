import os

DB_URL = os.getenv('DATABASE_URL', 'sqlite:///./civicgrid.db')
JWT_SECRET = os.getenv("JWT_SECRET", "utopia-super-secret-key-2026")
JWT_ALGORITHM = "HS256"

# Demo authorized municipal officers with Employee IDs (Badge IDs)
MUNICIPAL_USERS = {
    "admin@gcc.gov.in": {
        "password": "admin123",
        "name": "Er. S. Radhakrishnan",
        "role": "admin",
        "department": "Greater Chennai Corporation",
        "designation": "Superintending Engineer (Works)",
        "badge_id": "GCC-ENG-0842"
    },
    "water@metrowater.tn.gov.in": {
        "password": "water123",
        "name": "Dr. V. Meenakshi",
        "role": "official",
        "department": "Chennai Metro Water",
        "designation": "Executive Engineer (Pipelines)",
        "badge_id": "CMW-DIV-0219"
    },
    "roads@gcc.gov.in": {
        "password": "roads123",
        "name": "Er. K. Ramanathan",
        "role": "official",
        "department": "GCC Roads & Bridges",
        "designation": "Divisional Engineer (Zone 10)",
        "badge_id": "GCC-RD-0155"
    },
    "power@tangedco.gov.in": {
        "password": "power123",
        "name": "Er. Anitha Selvan",
        "role": "official",
        "department": "TANGEDCO",
        "designation": "Assistant Executive Engineer (O&M)",
        "badge_id": "TNEB-AEE-4091"
    },
    "drainage@gcc.gov.in": {
        "password": "drain123",
        "name": "Er. M. Gunasekaran",
        "role": "official",
        "department": "Stormwater Drainage",
        "designation": "Executive Engineer (SWD)",
        "badge_id": "SWD-ENG-1102"
    },
    "field.gcc@chennai.gov.in": {
        "password": "field123",
        "name": "M. Selvam",
        "role": "onsite",
        "department": "GCC Roads & Bridges",
        "designation": "Field Supervisor (Zone 10)",
        "badge_id": "GCC-FIELD-552"
    },
    "field.water@metrowater.tn.gov.in": {
        "password": "field123",
        "name": "R. Prakash",
        "role": "onsite",
        "department": "Chennai Metro Water",
        "designation": "Site Trenching Foreman",
        "badge_id": "CMW-SITE-884"
    },
    "field.power@tangedco.gov.in": {
        "password": "field123",
        "name": "S. Kumar",
        "role": "onsite",
        "department": "TANGEDCO",
        "designation": "Field Line & Cable Engineer",
        "badge_id": "TNEB-SITE-312"
    }
}
