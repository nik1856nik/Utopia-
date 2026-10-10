import re
import json
import urllib.request
from typing import Dict, Any

# Fast cached offline centroid coordinates for Chennai PIN codes
PINCODE_CACHE: Dict[str, Dict[str, Any]] = {
    "600127": {"locality": "Melakottaiyur", "lat": 12.8436, "lng": 80.1534},
    "600005": {"locality": "Triplicane", "lat": 13.0592, "lng": 80.2770},
    "600023": {"locality": "Ayanavaram", "lat": 13.0983, "lng": 80.2337},
    "600017": {"locality": "T. Nagar", "lat": 13.0418, "lng": 80.2341},
    "600004": {"locality": "Mylapore", "lat": 13.0339, "lng": 80.2677},
    "600001": {"locality": "George Town / Parrys", "lat": 13.0931, "lng": 80.2867},
    "600002": {"locality": "Anna Salai / Mount Road", "lat": 13.0674, "lng": 80.2707},
    "600028": {"locality": "R.A. Puram", "lat": 13.0232, "lng": 80.2570},
    "600034": {"locality": "Nungambakkam", "lat": 13.0604, "lng": 80.2405},
    "600040": {"locality": "Anna Nagar", "lat": 13.0850, "lng": 80.2101},
    "600041": {"locality": "Thiruvanmiyur", "lat": 12.9830, "lng": 80.2594},
    "600096": {"locality": "Perungudi OMR", "lat": 12.9654, "lng": 80.2461},
    "600119": {"locality": "Sholinganallur", "lat": 12.9010, "lng": 80.2279},
    "600042": {"locality": "Velachery", "lat": 12.9750, "lng": 80.2206},
    "600083": {"locality": "Ashok Nagar", "lat": 13.0354, "lng": 80.2117},
}

def resolve_pincode_coordinates(clean_pin: str) -> Dict[str, Any]:
    if clean_pin in PINCODE_CACHE:
        return PINCODE_CACHE[clean_pin]

    # Attempt OpenStreetMap Nominatim resolution
    try:
        url = f"https://nominatim.openstreetmap.org/search?postalcode={clean_pin}&country=India&format=json&limit=1"
        req = urllib.request.Request(url, headers={"User-Agent": "UtopiaSmartWorks/2.0 (contact@utopiamunicipal.gov.in)"})
        with urllib.request.urlopen(req, timeout=3.5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if data and len(data) > 0:
                first = data[0]
                lat = float(first["lat"])
                lng = float(first["lon"])
                disp = first.get("display_name", "")
                loc_name = disp.split(",")[0].strip() if disp else f"Zone PIN {clean_pin}"
                res = {"locality": loc_name, "lat": lat, "lng": lng}
                PINCODE_CACHE[clean_pin] = res
                return res
    except Exception:
        pass

    # Generic Chennai metro centroid fallback
    fallback = {"locality": f"Chennai Postal Sector {clean_pin}", "lat": 13.0827, "lng": 80.2707}
    PINCODE_CACHE[clean_pin] = fallback
    return fallback
