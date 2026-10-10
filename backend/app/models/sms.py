from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, DateTime, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from ..database import Base

class SMSLog(Base):
    __tablename__ = 'sms_logs'
    id: Mapped[int] = mapped_column(primary_key=True)
    phone: Mapped[str] = mapped_column(String(20))
    pincode: Mapped[str] = mapped_column(String(6))
    message: Mapped[str] = mapped_column(Text)
    created: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
