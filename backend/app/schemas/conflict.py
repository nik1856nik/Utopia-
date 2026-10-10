from datetime import date
from typing import Optional
from pydantic import BaseModel

class ConflictCheckIn(BaseModel):
    start_date: date
    due_date: date
    lat: Optional[float] = None
    lng: Optional[float] = None
    pincode: Optional[str] = None
    locality: Optional[str] = None

class ConflictTicketIn(BaseModel):
    proposed_title: str
    proposed_category: Optional[str] = "Road Infrastructure"
    proposed_description: Optional[str] = ""
    proposed_budget: Optional[int] = 0
    proposed_start: date
    proposed_end: date
    proposed_locality: str
    proposed_pincode: Optional[str] = None
    ward_id: Optional[int] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    reason_for_proceeding: str
    conflicting_project_id: Optional[int] = None
    conflicting_dept: str
    conflicting_project_title: str
    conflicting_start: Optional[date] = None
    conflicting_end: Optional[date] = None

class ConflictResolveIn(BaseModel):
    approved_dept: str  # Which department is chosen to proceed with work
    decision: str       # Municipality official rationale / instructions

class ConflictRescheduleIn(BaseModel):
    new_start_date: date
    new_due_date: date
