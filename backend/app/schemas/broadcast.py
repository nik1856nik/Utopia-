from typing import Optional, List
from pydantic import BaseModel

class WhatsAppBroadcastIn(BaseModel):
    pincode: str
    message: str
    target_count: Optional[int] = 2500
    category: Optional[str] = "Municipal Traffic & Work Advisory"

class BroadcastResponse(BaseModel):
    success: bool
    ref: str
    pincode: str
    recipients_count: int
    message: str
    channels: List[str]
