from typing import Optional
from pydantic import BaseModel

class IssueIn(BaseModel):
    project_id: Optional[int] = None
    kind: str
    department: Optional[str] = None
    message: str
    phone: Optional[str] = None
    email: Optional[str] = None
    severity: Optional[str] = 'Normal'
    locality: Optional[str] = 'Chennai'
    pincode: Optional[str] = None
    is_question: Optional[bool] = False
    intimated_in_advance: Optional[bool] = False

class IssueReplyIn(BaseModel):
    reply: str
    status: str = 'Resolved'

class QuestionIn(BaseModel):
    project_id: int
    message: str
    phone: Optional[str] = None
    email: Optional[str] = None
