from typing import Optional
from pydantic import BaseModel

class IssueIn(BaseModel):
    project_id: Optional[int] = None
    kind: str
    department: str
    message: str
    phone: Optional[str] = None
    email: Optional[str] = None
    severity: Optional[str] = 'Normal'
    locality: str
    pincode: Optional[str] = None

class IssueReplyIn(BaseModel):
    reply: str
    status: str = 'Resolved'

class QuestionIn(BaseModel):
    project_id: int
    message: str
    phone: Optional[str] = None
    email: Optional[str] = None
