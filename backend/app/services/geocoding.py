import re
import json
import threading
import time
from functools import lru_cache
from urllib.parse import urlencode
import urllib.request
from typing import Dict, Any
from ..config import NOMINATIM_BASE_URL, NOMINATIM_USER_AGENT

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

_reverse_lock = threading.Lock()
_last_reverse_request = 0.0


@lru_cache(maxsize=512)
def _reverse_geocode_cached(lat: float, lng: float) -> Dict[str, Any]:
    """Resolve coordinates through OSM Nominatim, caching nearby repeat calls."""
    global _last_reverse_request
    params = urlencode({"lat": lat, "lon": lng, "format": "jsonv2", "addressdetails": 1})
    request = urllib.request.Request(
        f"{NOMINATIM_BASE_URL}/reverse?{params}",
        headers={"User-Agent": NOMINATIM_USER_AGENT},
    )
    # Nominatim's public endpoint asks clients to keep requests at or below one
    # per second. Serialize requests so concurrent location lookups respect it.
    with _reverse_lock:
        wait = 1.0 - (time.monotonic() - _last_reverse_request)
        if wait > 0:
            time.sleep(wait)
        try:
            with urllib.request.urlopen(request, timeout=5.0) as response:
                data = json.loads(response.read().decode("utf-8"))
        finally:
            _last_reverse_request = time.monotonic()

    address = data.get("address") or {}
    locality = next((
        address.get(key) for key in (
            "neighbourhood", "suburb", "quarter", "city_district", "town", "city", "village"
        ) if address.get(key)
    ), None)
    if not locality:
        locality = (data.get("display_name") or "").split(",", 1)[0].strip() or "Selected location"

    raw_pin = str(address.get("postcode") or "")
    match = re.search(r"(?<!\d)(\d{6})(?!\d)", raw_pin)
    pincode = match.group(1) if match and str(address.get("country_code") or "").lower() == "in" else None
    return {"locality": locality, "pincode": pincode, "lat": lat, "lng": lng}


def reverse_geocode_coordinates(lat: float, lng: float) -> Dict[str, Any]:
    # Coordinate rounding coalesces tiny GPS differences and improves cache hits.
    return _reverse_geocode_cached(round(lat, 5), round(lng, 5))

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
