from typing import Optional
from pydantic import BaseModel

class LoginRequest(BaseModel):
    employee_id: Optional[str] = None
    email: Optional[str] = None
    password: str
    department: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict
