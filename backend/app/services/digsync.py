from typing import List, Dict, Any
from sqlalchemy.orm import Session
from ..models.project import Project

def detect_digsync_conflicts(s: Session) -> List[Dict[str, Any]]:
    """Detect potential corridor collision & simultaneous digging conflicts between different utilities."""
    projects = s.query(Project).filter(
        Project.status.in_(['In progress', 'Scheduled', 'Delayed', 'Upcoming'])
    ).all()

    conflicts = []
    for i in range(len(projects)):
        for j in range(i + 1, len(projects)):
            a, b = projects[i], projects[j]
            # Skip same department
            if a.department == b.department:
                continue

            # Distance in km (rough spherical estimation for Chennai coordinate span)
            dist = ((a.lat - b.lat)**2 + (a.lng - b.lng)**2)**0.5 * 111.0
            
            # Check proximity within 1.5 km corridor
            if dist < 1.5:
                start_a, due_a = a.start_date, (a.revised_date or a.due_date)
                start_b, due_b = b.start_date, (b.revised_date or b.due_date)

                # Overlap calculation
                latest_start = max(start_a, start_b)
                earliest_end = min(due_a, due_b)
                gap = (earliest_end - latest_start).days

                # Conflicts within 45 days window
                if gap >= -45:
                    is_high = gap >= 0 and dist < 0.8
                    conflicts.append({
                        'id': f"DS-{a.id}-{b.id}",
                        'locality': a.locality,
                        'distance_meters': int(dist * 1000),
                        'overlap_days': gap if gap > 0 else 0,
                        'severity': 'High Conflict' if is_high else 'Potential Conflict',
                        'overlap_type': 'Trenching / Road Resurfacing Collision' if ('Road' in a.category or 'Road' in b.category) else 'Simultaneous Right-of-Way Excavation',
                        'projects': [
                            {'id': a.id, 'code': a.code, 'title': a.title, 'department': a.department, 'status': a.status, 'start_date': a.start_date.isoformat(), 'due_date': (a.revised_date or a.due_date).isoformat(), 'address': a.address},
                            {'id': b.id, 'code': b.code, 'title': b.title, 'department': b.department, 'status': b.status, 'start_date': b.start_date.isoformat(), 'due_date': (b.revised_date or b.due_date).isoformat(), 'address': b.address}
                        ],
                        'reason': f'{a.locality} corridor: {a.department} ({a.category}) & {b.department} ({b.category}) overlap within {int(dist * 1000)}m and {gap} days of each other.'
                    })
    return conflicts
