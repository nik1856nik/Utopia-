import re
from fastapi import APIRouter, HTTPException, Query
from ..services.geocoding import resolve_pincode_coordinates, reverse_geocode_coordinates

router = APIRouter(prefix="/api/geocode", tags=["Geocoding & Location"])

@router.get('/pincode')
def geocode_pincode(pin: str = Query(..., description="6-digit Indian Postal Code")):
    clean = re.sub(r'\D', '', pin.strip())
    if len(clean) != 6:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid PIN code '{pin}'. Indian postal codes must contain exactly 6 digits."
        )
    return resolve_pincode_coordinates(clean)

@router.get('/reverse')
def reverse_geocode(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
):
    try:
        return reverse_geocode_coordinates(lat, lng)
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Reverse geocoding is temporarily unavailable.") from exc
