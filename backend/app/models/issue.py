from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from ..database import Base

class Issue(Base):
    __tablename__ = 'issues'
    id: Mapped[int] = mapped_column(primary_key=True)
    ref: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    project_id: Mapped[Optional[int]] = mapped_column(ForeignKey('projects.id'), nullable=True, index=True)
    kind: Mapped[str] = mapped_column(String(180))
    department: Mapped[Optional[str]] = mapped_column(String(100), default='Greater Chennai Corporation', nullable=True)
    message: Mapped[str] = mapped_column(Text)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default='Open')
    severity: Mapped[str] = mapped_column(String(20), default='Normal')
    locality: Mapped[str] = mapped_column(String(100))
    pincode: Mapped[Optional[str]] = mapped_column(String(6), nullable=True)
    is_question: Mapped[bool] = mapped_column(Boolean, default=False)
    intimated_in_advance: Mapped[bool] = mapped_column(Boolean, default=False)
    created: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    official_reply: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    replied_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    replied_by: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
