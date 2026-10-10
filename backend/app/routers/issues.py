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
    ref = f'CGI-{(data.locality[:4] if data.locality else "CHEN").upper()}-{count + 1:04d}'
    
    # Auto-resolve department if associated with a project
    dept = data.department
    if data.project_id and not dept:
        proj = s.get(Project, data.project_id)
        if proj:
            dept = proj.department

    issue = Issue(
        ref=ref,
        project_id=data.project_id,
        kind=data.kind,
        department=dept or "Greater Chennai Corporation",
        message=data.message,
        phone=data.phone,
        email=data.email,
        severity=data.severity or 'Normal',
        locality=data.locality,
        pincode=data.pincode,
        status='Submitted',
        is_question=False
    )
    s.add(issue)
    s.commit()
    s.refresh(issue)
    return {
        'id': issue.id,
        'ref': issue.ref,
        'message': f'Issue registered successfully under reference {ref}.'
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
