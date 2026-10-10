from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.issue import Issue
from ..models.project import Project
from ..schemas.issue import IssueIn, IssueReplyIn, QuestionIn
from ..services.auth import get_current_user

router = APIRouter(prefix="/api", tags=["Citizen Issues & Inquiries"])

@router.get('/issues')
def list_issues(
    pincode: Optional[str] = None,
    locality: Optional[str] = None,
    department: Optional[str] = None,
    s: Session = Depends(get_db)
):
    q = s.query(Issue)
    if pincode:
        q = q.filter(Issue.pincode == pincode)
    if locality:
        q = q.filter(Issue.locality.ilike(f"%{locality}%"))
    if department:
        q = q.filter(Issue.department.ilike(f"%{department}%"))
    
    issues = q.order_by(Issue.created.desc()).all()
    out = []
    now = datetime.utcnow()
    for i in issues:
        days_elapsed = (now - i.created).days
        is_escalated = (i.status not in ['Resolved', 'Answered']) and (days_elapsed >= 3)
        out.append({
            'id': i.id,
            'ref': i.ref,
            'project_id': i.project_id,
            'kind': i.kind,
            'department': i.department,
            'message': i.message,
            'status': i.status,
            'severity': i.severity,
            'locality': i.locality,
            'pincode': i.pincode,
            'is_question': i.is_question,
            'intimated_in_advance': i.intimated_in_advance,
            'is_escalated': is_escalated,
            'days_elapsed': days_elapsed,
            'created': i.created.isoformat(),
            'official_reply': i.official_reply,
            'replied_at': i.replied_at.isoformat() if i.replied_at else None,
            'replied_by': i.replied_by
        })
    return out

@router.post('/issues')
def create_issue(data: IssueIn, s: Session = Depends(get_db)):
    count = s.query(Issue).count()
    
    # Auto-resolve department, locality, and pincode if associated with a project
    dept = data.department
    locality = data.locality or 'Chennai'
    pincode = data.pincode
    
    if data.project_id:
        proj = s.get(Project, data.project_id)
        if proj:
            if not dept:
                dept = proj.department
            if not pincode:
                pincode = proj.pincode
            if not locality or locality == 'Chennai':
                locality = proj.locality

    if not dept:
        k = f"{data.kind or ''} {data.message or ''}".lower()
        if "water" in k or "pipe" in k or "sewage" in k or "meter" in k:
            dept = "Chennai Metro Water"
        elif "power" in k or "electric" in k or "cable" in k or "wire" in k or "tangedco" in k or "transformer" in k:
            dept = "TANGEDCO"
        elif "stormwater" in k or "flood" in k or "swd" in k or "drain" in k or "culvert" in k:
            dept = "Stormwater Drainage"
        elif "road" in k or "pothole" in k or "asphalt" in k or "tar" in k or "walkway" in k or "pavement" in k:
            dept = "GCC Roads & Bridges"
        else:
            dept = "Greater Chennai Corporation"

    prefix = "Q" if data.is_question else "CGI"
    ref = f'{prefix}-{(locality[:4] if locality else "CHEN").upper()}-{count + 1:04d}'

    issue = Issue(
        ref=ref,
        project_id=data.project_id,
        kind=data.kind,
        department=dept,
        message=data.message,
        phone=data.phone,
        email=data.email,
        severity=data.severity or 'Normal',
        locality=locality,
        pincode=pincode,
        status='Submitted',
        is_question=bool(data.is_question),
        intimated_in_advance=bool(data.intimated_in_advance)
    )
    s.add(issue)
    s.commit()
    s.refresh(issue)
    return {
        'id': issue.id,
        'ref': issue.ref,
        'department': issue.department,
        'message': f'{"Question" if issue.is_question else "Issue"} registered and routed to {issue.department}. Reference: {ref}'
    }

@router.post('/ask-question')
def ask_question(data: QuestionIn, s: Session = Depends(get_db)):
    proj = s.get(Project, data.project_id)
    if not proj:
        raise HTTPException(404, 'Project not found')
    
    count = s.query(Issue).count()
    ref = f'Q-{(proj.locality[:4] if proj.locality else "CHEN").upper()}-{count + 1:04d}'

    issue = Issue(
        ref=ref,
        project_id=proj.id,
        kind=f"Public Question regarding {proj.title}",
        department=proj.department,
        message=data.message,
        phone=data.phone,
        email=data.email,
        locality=proj.locality,
        pincode=proj.pincode,
        status='Submitted',
        is_question=True
    )
    s.add(issue)
    s.commit()
    return {
        'id': issue.id,
        'ref': issue.ref,
        'message': f'Your question has been forwarded to {proj.department}. Reference: {ref}'
    }

@router.post('/issues/{issue_id}/reply')
def reply_issue(issue_id: int, payload: IssueReplyIn, user: dict = Depends(get_current_user), s: Session = Depends(get_db)):
    issue = s.get(Issue, issue_id)
    if not issue:
        raise HTTPException(404, 'Issue not found')
    
    issue.official_reply = payload.reply
    issue.status = payload.status or 'Answered'
    issue.replied_at = datetime.utcnow()
    issue.replied_by = f"{user.get('name', 'Municipal Engineer')} ({user.get('badge_id', 'GCC')})"
    s.commit()
    return {
        'id': issue.id,
        'status': issue.status,
        'official_reply': issue.official_reply,
        'replied_at': issue.replied_at.isoformat(),
        'replied_by': issue.replied_by
    }
