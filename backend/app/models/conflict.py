from datetime import date, datetime
from typing import Optional
from sqlalchemy import String, Integer, Float, Date, DateTime, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from ..database import Base

class ConflictTicket(Base):
    """Raised when a department wants to proceed despite a scheduling conflict."""
    __tablename__ = 'conflict_tickets'
    id: Mapped[int] = mapped_column(primary_key=True)
    ref: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    # Requesting department info
    requesting_dept: Mapped[str] = mapped_column(String(100))
    requesting_officer: Mapped[str] = mapped_column(String(120))
    requesting_badge: Mapped[str] = mapped_column(String(40))
    proposed_title: Mapped[str] = mapped_column(String(200))
    proposed_category: Mapped[Optional[str]] = mapped_column(String(100), default='Road Infrastructure')
    proposed_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    proposed_budget: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    proposed_start: Mapped[date] = mapped_column(Date)
    proposed_end: Mapped[date] = mapped_column(Date)
    proposed_locality: Mapped[str] = mapped_column(String(100))
    proposed_pincode: Mapped[Optional[str]] = mapped_column(String(6), nullable=True)
    ward_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    lat: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    lng: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    requesting_project_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    reason_for_proceeding: Mapped[str] = mapped_column(Text)  # why dept must proceed despite conflict
    # Conflicting project info
    conflicting_project_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    conflicting_dept: Mapped[str] = mapped_column(String(100))
    conflicting_project_title: Mapped[str] = mapped_column(String(200))
    conflicting_start: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    conflicting_end: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    # Ticket status & municipality resolution
    status: Mapped[str] = mapped_column(String(40), default='Pending')  # Pending, Reviewing, Resolved
    approved_dept: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # Dept chosen to proceed
    municipality_decision: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Official rationale/notes
    resolved_by: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    # Rescheduling fields for non-approved department
    rescheduled_dept: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    rescheduled_start: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    rescheduled_end: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    rescheduled_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # Pending Reschedule, Scheduled
    # Notification flags
    requesting_dept_notified: Mapped[bool] = mapped_column(Boolean, default=False)
    conflicting_dept_notified: Mapped[bool] = mapped_column(Boolean, default=False)
    created: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
