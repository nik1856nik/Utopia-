from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from ..database import Base

class FieldSubmission(Base):
    __tablename__ = 'field_submissions'
    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey('projects.id'))
    official_name: Mapped[str] = mapped_column(String(120))
    official_badge: Mapped[str] = mapped_column(String(40))
    official_dept: Mapped[str] = mapped_column(String(100))
    report_type: Mapped[str] = mapped_column(String(50))  # 'progress', 'blocker', 'photo', 'shift_log', 'delay'
    summary: Mapped[str] = mapped_column(String(200))
    detail: Mapped[str] = mapped_column(Text)
    progress_pct: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    step_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    photo_url: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    photo_caption: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    severity: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    labor_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    machinery_deployed: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    shift_hours: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default='Submitted')
    created: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
