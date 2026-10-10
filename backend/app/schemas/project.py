from datetime import date
from typing import Optional, List
from pydantic import BaseModel
from ..models.project import Project

class ProjectCreateIn(BaseModel):
    title: str
    category: str
    department: Optional[str] = None
    locality: str
    pincode: str
    address: Optional[str] = None
    description: str
    budget: int
    contractor: Optional[str] = "Pending Tender Award"
    start_date: date
    due_date: date
    lat: Optional[float] = None
    lng: Optional[float] = None
    disruption: Optional[str] = "Standard lane traffic diversion"
    contact_engineer_name: Optional[str] = "Er. K. Ramanathan"
    contact_engineer_phone: Optional[str] = "+91 94440 28192"
    contact_engineer_email: Optional[str] = "engineer.civicworks@chennaicorporation.gov.in"
    contact_contractor: Optional[str] = "MetroLink Infrastructure Ltd."
    contact_contractor_phone: Optional[str] = "+91 98841 55210"
    noise_warning: Optional[str] = "Permitted high-noise window: 22:00 - 04:00"
    dust_warning: Optional[str] = "Trenching dust window: 09:00 - 14:00"
    gmaps_broadcast: Optional[bool] = True
    detour_advice: Optional[str] = "Traffic diversion via Panagal Park"
    technical_scope: Optional[str] = None
    funding_program: Optional[str] = "Municipal Infrastructure Capital Fund"

class ProjectUpdateIn(BaseModel):
    status: Optional[str] = None
    progress: Optional[int] = None
    revised_date: Optional[date] = None
    delay_reason: Optional[str] = None
    mitigation: Optional[str] = None
    current_step: Optional[int] = None
    contact_engineer_name: Optional[str] = None
    contact_engineer_phone: Optional[str] = None
    contact_engineer_email: Optional[str] = None
    contact_contractor: Optional[str] = None
    contact_contractor_phone: Optional[str] = None
    noise_warning: Optional[str] = None
    dust_warning: Optional[str] = None
    gmaps_broadcast: Optional[bool] = None
    detour_advice: Optional[str] = None
    technical_scope: Optional[str] = None
    funding_program: Optional[str] = None

class EventIn(BaseModel):
    title: str
    detail: str

def serialize_project(p: Project):
    return {
        'id': p.id,
        'code': p.code,
        'title': p.title,
        'category': p.category,
        'department': p.department,
        'locality': p.locality,
        'pincode': p.pincode,
        'address': p.address,
        'description': p.description,
        'status': p.status,
        'progress': p.progress,
        'budget': p.budget,
        'contractor': p.contractor,
        'start_date': p.start_date.isoformat() if p.start_date else None,
        'due_date': p.due_date.isoformat() if p.due_date else None,
        'revised_date': p.revised_date.isoformat() if p.revised_date else None,
        'lat': p.lat,
        'lng': p.lng,
        'disruption': p.disruption,
        'delay_reason': p.delay_reason,
        'mitigation': p.mitigation,
        'updated': p.updated.isoformat(),
        'current_step': p.current_step,
        'contact_engineer_name': p.contact_engineer_name,
        'contact_engineer_phone': p.contact_engineer_phone,
        'contact_engineer_email': p.contact_engineer_email,
        'contact_contractor': p.contact_contractor,
        'contact_contractor_phone': p.contact_contractor_phone,
        'noise_warning': p.noise_warning,
        'dust_warning': p.dust_warning,
        'gmaps_broadcast': p.gmaps_broadcast,
        'detour_advice': p.detour_advice,
        'technical_scope': p.technical_scope,
        'funding_program': p.funding_program,
        'created_by': p.created_by
    }
