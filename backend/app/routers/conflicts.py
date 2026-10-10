from datetime import datetime, date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.project import Project, Event
from ..models.conflict import ConflictTicket
from ..schemas.conflict import ConflictCheckIn, ConflictTicketIn, ConflictResolveIn, ConflictRescheduleIn
from ..services.auth import get_current_user
from ..services.digsync import detect_digsync_conflicts

router = APIRouter(prefix="/api", tags=["Conflict Resolution & DigSync"])

@router.get('/digsync')
def get_digsync_conflicts(s: Session = Depends(get_db)):
    return detect_digsync_conflicts(s)

@router.post('/projects/check-conflicts')
def check_schedule_conflicts(payload: ConflictCheckIn, user: dict = Depends(get_current_user), s: Session = Depends(get_db)):
    """Check if a proposed project schedule conflicts with existing projects from other departments."""
    dept = user.get('department', '')
    items = s.query(Project).filter(
        Project.status.in_(['Scheduled', 'In progress', 'Delayed', 'Upcoming'])
    ).all()

    found = []
    for proj in items:
        # Skip projects from same department
        if dept and dept.lower() in proj.department.lower():
            continue
        # Date overlap check: two ranges [s1,e1] and [s2,e2] overlap if s1 <= e2 and s2 <= e1
        p_end = proj.revised_date or proj.due_date
        date_overlap = (payload.start_date <= p_end) and (proj.start_date <= payload.due_date)
        if not date_overlap:
            continue
        # Spatial check if lat/lng provided
        if payload.lat and payload.lng and proj.lat and proj.lng:
            dist_km = ((payload.lat - proj.lat)**2 + (payload.lng - proj.lng)**2)**0.5 * 111
            if dist_km > 2.0:
                continue  # too far apart, no conflict
        elif payload.pincode and proj.pincode:
            if payload.pincode != proj.pincode:
                continue  # different pincodes, skip
        
        # Conflict found
        overlap_days = (min(payload.due_date, p_end) - max(payload.start_date, proj.start_date)).days + 1
        found.append({
            'project_id': proj.id,
            'code': proj.code,
            'title': proj.title,
            'department': proj.department,
            'start_date': proj.start_date.isoformat(),
            'end_date': p_end.isoformat(),
            'status': proj.status,
            'locality': proj.locality,
            'overlap_days': overlap_days
        })
    return {'conflicts': found, 'total': len(found)}

@router.post('/conflict-tickets')
def raise_conflict_ticket(payload: ConflictTicketIn, user: dict = Depends(get_current_user), s: Session = Depends(get_db)):
    if user.get('role') not in ['official', 'admin']:
        raise HTTPException(403, 'Only department officials can raise conflict tickets')
    count = s.query(ConflictTicket).count()
    ref = f'CT-{datetime.now():%y%m%d}-{count+1:04d}'
    ticket = ConflictTicket(
        ref=ref,
        requesting_dept=user.get('department', ''),
        requesting_officer=user.get('name', ''),
        requesting_badge=user.get('badge_id', ''),
        proposed_title=payload.proposed_title,
        proposed_category=payload.proposed_category or "Road Infrastructure",
        proposed_description=payload.proposed_description or "",
        proposed_budget=payload.proposed_budget or 0,
        proposed_start=payload.proposed_start,
        proposed_end=payload.proposed_end,
        proposed_locality=payload.proposed_locality,
        proposed_pincode=payload.proposed_pincode,
        ward_id=payload.ward_id,
        lat=payload.lat,
        lng=payload.lng,
        reason_for_proceeding=payload.reason_for_proceeding,
        conflicting_project_id=payload.conflicting_project_id,
        conflicting_dept=payload.conflicting_dept,
        conflicting_project_title=payload.conflicting_project_title,
        conflicting_start=payload.conflicting_start,
        conflicting_end=payload.conflicting_end,
        status='Pending'
    )
    s.add(ticket)
    s.commit()
    s.refresh(ticket)
    return {
        'id': ticket.id,
        'ref': ticket.ref,
        'status': ticket.status,
        'message': f'Conflict ticket {ref} raised to Municipality for review.'
    }

@router.get('/conflict-tickets')
def get_conflict_tickets(user: dict = Depends(get_current_user), s: Session = Depends(get_db)):
    dept = user.get('department', '').lower()
    role = user.get('role', '')
    q = s.query(ConflictTicket)
    # Officials can only see their dept's tickets; admin/municipality sees all
    if role == 'official':
        q = q.filter(
            (ConflictTicket.requesting_dept.ilike(f'%{dept}%')) |
            (ConflictTicket.conflicting_dept.ilike(f'%{dept}%'))
        )
    tickets = q.order_by(ConflictTicket.created.desc()).all()
    return [{
        'id': t.id,
        'ref': t.ref,
        'requesting_dept': t.requesting_dept,
        'requesting_officer': t.requesting_officer,
        'requesting_badge': t.requesting_badge,
        'proposed_title': t.proposed_title,
        'proposed_category': t.proposed_category,
        'proposed_description': t.proposed_description,
        'proposed_budget': t.proposed_budget,
        'proposed_start': t.proposed_start.isoformat() if t.proposed_start else None,
        'proposed_end': t.proposed_end.isoformat() if t.proposed_end else None,
        'proposed_locality': t.proposed_locality,
        'proposed_pincode': t.proposed_pincode,
        'reason_for_proceeding': t.reason_for_proceeding,
        'conflicting_project_id': t.conflicting_project_id,
        'conflicting_dept': t.conflicting_dept,
        'conflicting_project_title': t.conflicting_project_title,
        'conflicting_start': t.conflicting_start.isoformat() if t.conflicting_start else None,
        'conflicting_end': t.conflicting_end.isoformat() if t.conflicting_end else None,
        'status': t.status,
        'approved_dept': t.approved_dept,
        'municipality_decision': t.municipality_decision,
        'resolved_by': t.resolved_by,
        'resolved_at': t.resolved_at.isoformat() if t.resolved_at else None,
        'rescheduled_dept': t.rescheduled_dept,
        'rescheduled_start': t.rescheduled_start.isoformat() if t.rescheduled_start else None,
        'rescheduled_end': t.rescheduled_end.isoformat() if t.rescheduled_end else None,
        'rescheduled_status': t.rescheduled_status,
        'requesting_dept_notified': t.requesting_dept_notified,
        'conflicting_dept_notified': t.conflicting_dept_notified,
        'created': t.created.isoformat()
    } for t in tickets]

@router.patch('/conflict-tickets/{ticket_id}/resolve')
@router.post('/conflict-tickets/{ticket_id}/resolve')
def resolve_conflict_ticket(ticket_id: int, payload: ConflictResolveIn, user: dict = Depends(get_current_user), s: Session = Depends(get_db)):
    if user.get('role') != 'admin':
        raise HTTPException(403, 'Only Municipality administrators can resolve conflict tickets')
    ticket = s.get(ConflictTicket, ticket_id)
    if not ticket:
        raise HTTPException(404, 'Conflict ticket not found')
    
    ticket.status = 'Resolved'
    ticket.approved_dept = payload.approved_dept
    ticket.municipality_decision = payload.decision
    ticket.resolved_by = f"{user.get('name')} ({user.get('badge_id')})"
    ticket.resolved_at = datetime.utcnow()
    ticket.requesting_dept_notified = True
    ticket.conflicting_dept_notified = True

    # Determine which department won approval and which must reschedule
    is_requesting_approved = payload.approved_dept.strip().lower() in ticket.requesting_dept.lower() or ticket.requesting_dept.lower() in payload.approved_dept.strip().lower()

    if is_requesting_approved:
        ticket.approved_dept = ticket.requesting_dept
        ticket.rescheduled_dept = ticket.conflicting_dept
        ticket.rescheduled_status = 'Pending Reschedule'

        # Auto-create or update requesting department project to 'In progress'
        if ticket.requesting_project_id:
            req_proj = s.get(Project, ticket.requesting_project_id)
            if req_proj:
                req_proj.status = 'In progress'
                req_proj.progress = max(req_proj.progress, 15)
        else:
            p_count = s.query(Project).count()
            p_code = f"CG-2026-{p_count+1:03d}"
            req_proj = Project(
                code=p_code,
                title=ticket.proposed_title,
                category=ticket.proposed_category or "Road Infrastructure",
                department=ticket.requesting_dept,
                locality=ticket.proposed_locality or "Chennai",
                pincode=ticket.proposed_pincode or "600001",
                address=f"{ticket.proposed_locality}, Chennai",
                description=ticket.proposed_description or ticket.reason_for_proceeding,
                budget=ticket.proposed_budget or 1000000,
                contractor="Approved by Municipal Priority Order",
                start_date=ticket.proposed_start,
                due_date=ticket.proposed_end,
                status="In progress",
                progress=15,
                lat=ticket.lat or 13.0418,
                lng=ticket.lng or 80.2341,
                disruption="Standard single-lane diversion",
                created_by=ticket.requesting_officer or user.get('name')
            )
            s.add(req_proj)
            s.flush()
            ticket.requesting_project_id = req_proj.id
            ev = Event(
                project_id=req_proj.id,
                title="Conflict Resolved — Priority Sanction",
                detail=f"Approved to proceed In Progress by {user.get('name')}. Direction: {payload.decision}",
                created=datetime.utcnow(),
                verified=True
            )
            s.add(ev)

        # Update conflicting project status
        if ticket.conflicting_project_id:
            conf_proj = s.get(Project, ticket.conflicting_project_id)
            if conf_proj:
                conf_proj.status = 'Rescheduling Required'

    else:
        ticket.approved_dept = ticket.conflicting_dept
        ticket.rescheduled_dept = ticket.requesting_dept
        ticket.rescheduled_status = 'Pending Reschedule'

        # Set conflicting project to 'In progress'
        if ticket.conflicting_project_id:
            conf_proj = s.get(Project, ticket.conflicting_project_id)
            if conf_proj:
                conf_proj.status = 'In progress'
                ev = Event(
                    project_id=conf_proj.id,
                    title="Conflict Resolved — Priority Confirmed",
                    detail=f"Municipality affirmed In Progress status by {user.get('name')}. Direction: {payload.decision}",
                    created=datetime.utcnow(),
                    verified=True
                )
                s.add(ev)

    s.commit()
    return {
        'id': ticket.id,
        'ref': ticket.ref,
        'status': ticket.status,
        'approved_dept': ticket.approved_dept,
        'rescheduled_dept': ticket.rescheduled_dept,
        'rescheduled_status': ticket.rescheduled_status,
        'municipality_decision': ticket.municipality_decision,
        'resolved_by': ticket.resolved_by,
        'resolved_at': ticket.resolved_at.isoformat()
    }

@router.post('/conflict-tickets/{ticket_id}/reschedule')
def reschedule_conflict_ticket(ticket_id: int, payload: ConflictRescheduleIn, user: dict = Depends(get_current_user), s: Session = Depends(get_db)):
    ticket = s.get(ConflictTicket, ticket_id)
    if not ticket:
        raise HTTPException(404, 'Conflict ticket not found')
    if ticket.status != 'Resolved':
        raise HTTPException(400, 'Ticket must be resolved by Municipality before rescheduling')

    dept = ticket.rescheduled_dept or user.get('department', '')

    # Check for conflicts with other departments for these new proposed dates
    all_projects = s.query(Project).filter(
        Project.status.in_(['Scheduled', 'In progress', 'Delayed', 'Upcoming'])
    ).all()

    for proj in all_projects:
        # Skip same department and skip self
        if dept and dept.lower() in proj.department.lower():
            continue
        
        # Skip the project of the department that is doing the rescheduling
        is_requesting_self = ticket.rescheduled_dept and ticket.rescheduled_dept.lower() in ticket.requesting_dept.lower()
        if is_requesting_self and ticket.requesting_project_id and proj.id == ticket.requesting_project_id:
            continue
        if (not is_requesting_self) and ticket.conflicting_project_id and proj.id == ticket.conflicting_project_id:
            continue
        
        p_end = proj.revised_date or proj.due_date
        date_overlap = (payload.new_start_date <= p_end) and (proj.start_date <= payload.new_due_date)
        if not date_overlap:
            continue
        
        # Check geographic proximity
        if ticket.proposed_pincode and proj.pincode and ticket.proposed_pincode == proj.pincode:
            raise HTTPException(400, f"Scheduling conflict detected with '{proj.department}' on '{proj.title}' ({proj.start_date} to {p_end}). Please select alternative dates.")

    # No conflict: apply new dates and set status to 'Scheduled'
    is_requesting = ticket.rescheduled_dept and ticket.rescheduled_dept.lower() in ticket.requesting_dept.lower()

    if is_requesting:
        if ticket.requesting_project_id:
            proj = s.get(Project, ticket.requesting_project_id)
            if proj:
                proj.start_date = payload.new_start_date
                proj.due_date = payload.new_due_date
                proj.status = 'Scheduled'
        else:
            p_count = s.query(Project).count()
            p_code = f"CG-2026-{p_count+1:03d}"
            proj = Project(
                code=p_code,
                title=ticket.proposed_title,
                category=ticket.proposed_category or "Road Infrastructure",
                department=ticket.requesting_dept,
                locality=ticket.proposed_locality or "Chennai",
                pincode=ticket.proposed_pincode or "600001",
                address=f"{ticket.proposed_locality}, Chennai",
                description=ticket.proposed_description or ticket.reason_for_proceeding,
                budget=ticket.proposed_budget or 1000000,
                contractor="Rescheduled Municipal Work Order",
                start_date=payload.new_start_date,
                due_date=payload.new_due_date,
                status="Scheduled",
                progress=0,
                lat=ticket.lat or 13.0418,
                lng=ticket.lng or 80.2341,
                disruption="Standard single-lane diversion",
                created_by=ticket.requesting_officer or user.get('name')
            )
            s.add(proj)
            s.flush()
            ticket.requesting_project_id = proj.id
            ev = Event(
                project_id=proj.id,
                title="Rescheduled Work Order Confirmed",
                detail=f"Rescheduled without conflicts for {payload.new_start_date} to {payload.new_due_date}. Status set to Scheduled.",
                created=datetime.utcnow(),
                verified=True
            )
            s.add(ev)
    else:
        if ticket.conflicting_project_id:
            proj = s.get(Project, ticket.conflicting_project_id)
            if proj:
                proj.start_date = payload.new_start_date
                proj.due_date = payload.new_due_date
                proj.status = 'Scheduled'
                ev = Event(
                    project_id=proj.id,
                    title="Rescheduled Work Order Confirmed",
                    detail=f"Rescheduled without conflicts for {payload.new_start_date} to {payload.new_due_date}. Status set to Scheduled.",
                    created=datetime.utcnow(),
                    verified=True
                )
                s.add(ev)

    ticket.rescheduled_start = payload.new_start_date
    ticket.rescheduled_end = payload.new_due_date
    ticket.rescheduled_status = 'Scheduled'
    s.commit()

    return {
        'success': True,
        'message': f'Work successfully rescheduled for {payload.new_start_date} to {payload.new_due_date}. Status updated to Scheduled.',
        'ticket_id': ticket.id,
        'rescheduled_status': 'Scheduled',
        'start_date': payload.new_start_date.isoformat(),
        'due_date': payload.new_due_date.isoformat()
    }
