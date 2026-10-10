from typing import Optional
from pydantic import BaseModel

class FieldSubmissionIn(BaseModel):
    project_id: int
    report_type: str  # 'progress', 'blocker', 'photo', 'shift_log', 'delay'
    summary: str
    detail: str
    progress_pct: Optional[int] = None
    step_number: Optional[int] = None
    photo_url: Optional[str] = None
    photo_caption: Optional[str] = None
    severity: Optional[str] = None
    labor_count: Optional[int] = None
    machinery_deployed: Optional[str] = None
    shift_hours: Optional[str] = None
