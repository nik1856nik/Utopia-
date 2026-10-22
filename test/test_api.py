"""HTTP-level coverage for every FastAPI route and important route branch."""
from datetime import date

import pytest


def test_auth_login_profile_and_department_enforcement(client, auth_headers):
    assert client.get("/api/auth/me", headers=auth_headers).status_code == 200
    bad = client.post("/api/auth/login", json={"employee_id": "unknown", "password": "bad"})
    assert bad.status_code == 401
    mismatch = client.post("/api/auth/login", json={
        "employee_id": "CMW-DIV-0219", "password": "water123", "department": "Stormwater Drainage"
    })
    assert mismatch.status_code == 403
    assert client.get("/api/auth/me").status_code == 401


def test_project_directory_detail_create_update_and_event(client, make_project, auth_headers):
    project = make_project()
    assert len(client.get("/api/projects").json()) == 1
    assert client.get("/api/projects?department=Water").json()[0]["id"] == project.id
    assert client.get("/api/projects?pincode=600017").json()
    assert client.get("/api/projects?search=Test").json()
    assert client.get("/api/projects?locality=T.%20Nagar&status=In%20progress&category=Drainage").json()
    assert client.get(f"/api/projects/{project.id}").json()["id"] == project.id
    assert client.get("/api/projects/99999").status_code == 404

    payload = {
        "title": "Water renewal", "category": "Pipes", "department": "GCC Roads & Bridges",
        "locality": "T. Nagar", "pincode": "600017", "description": "Renew line", "budget": 1000,
        "start_date": "2026-01-01", "due_date": "2026-12-01",
    }
    created = client.post("/api/projects", json=payload, headers=auth_headers)
    assert created.status_code == 200
    assert created.json()["department"] == "Chennai Metro Water"
    assert client.patch(f"/api/projects/{project.id}", json={"progress": 75}, headers=auth_headers).json()["progress"] == 75
    event = client.post(f"/api/projects/{project.id}/events?title=Inspection&detail=Passed", headers=auth_headers)
    assert event.status_code == 200
    assert len(client.get(f"/api/projects/{project.id}").json()["events"]) == 1
    assert client.post("/api/projects", json=payload).status_code == 401
    assert client.patch("/api/projects/99999", json={"progress": 1}, headers=auth_headers).status_code == 404
    assert client.post(f"/api/projects/{project.id}/events?title=x&detail=y").status_code == 401


def test_project_department_boundary_for_officer(client, make_project):
    project = make_project(department="GCC Roads & Bridges")
    roads = client.post("/api/auth/login", json={"employee_id": "GCC-RD-0155", "password": "roads123"}).json()["access_token"]
    water = client.post("/api/auth/login", json={"employee_id": "CMW-DIV-0219", "password": "water123"}).json()["access_token"]
    assert client.patch(f"/api/projects/{project.id}", json={"progress": 5}, headers={"Authorization": f"Bearer {water}"}).status_code == 403
    assert client.patch(f"/api/projects/{project.id}", json={"progress": 5}, headers={"Authorization": f"Bearer {roads}"}).status_code == 200


@pytest.mark.xfail(strict=True, reason="Known issue: onsite JWTs currently bypass project role/department authorization")
def test_onsite_user_must_not_patch_an_unassigned_project(client, make_project):
    project = make_project(department="Chennai Metro Water")
    field = client.post("/api/auth/login", json={"employee_id": "GCC-FIELD-552", "password": "field123"}).json()["access_token"]
    response = client.patch(f"/api/projects/{project.id}", json={"progress": 1}, headers={"Authorization": f"Bearer {field}"})
    assert response.status_code == 403


def test_department_locality_and_statistics(client, make_project):
    make_project()
    assert "Chennai Metro Water" in client.get("/api/departments").json()
    assert client.get("/api/localities").json()[0]["pincode"] == "600017"
    stats = client.get("/api/stats?pincode=600017").json()
    assert stats["total"] == 1 and stats["total_budget"] == 100000
    assert client.get("/api/stats?pincode=999999").json()["total"] == 0


def test_citizen_issue_create_filter_question_and_official_reply(client, make_project, auth_headers):
    project = make_project()
    created = client.post("/api/issues", json={
        "project_id": project.id, "kind": "Water outage", "message": "No water", "phone": "9999999999"
    })
    assert created.status_code == 200
    issue_id = created.json()["id"]
    assert client.get("/api/issues?pincode=600017").json()[0]["id"] == issue_id
    question = client.post("/api/ask-question", json={"project_id": project.id, "message": "When done?"})
    assert question.status_code == 200
    assert client.get("/api/issues?department=Chennai%20Metro%20Water").json()
    assert client.get("/api/issues?locality=T.%20Nagar").json()
    reply = client.post(f"/api/issues/{issue_id}/reply", json={"reply": "We are investigating", "status": "Answered"}, headers=auth_headers)
    assert reply.status_code == 200
    assert reply.json()["status"] == "Answered"
    assert client.get(f"/api/projects/{project.id}").json()["issues"]
    assert client.post("/api/ask-question", json={"project_id": 99999, "message": "Question"}).status_code == 404
    assert client.post("/api/issues/99999/reply", json={"reply": "Reply"}, headers=auth_headers).status_code == 404


@pytest.mark.parametrize(("kind", "expected"), [
    ("water pipe leak", "Chennai Metro Water"),
    ("electric cable", "TANGEDCO"),
    pytest.param("stormwater drain", "Stormwater Drainage", marks=pytest.mark.xfail(strict=True, reason="Known issue: substring 'water' routes 'stormwater' complaints to Metro Water")),
    ("pothole road", "GCC Roads & Bridges"),
    ("general concern", "Greater Chennai Corporation"),
])
def test_issue_automatic_department_routing(client, kind, expected):
    response = client.post("/api/issues", json={"kind": kind, "message": "Please investigate", "locality": "Adyar"})
    assert response.status_code == 200
    assert response.json()["department"] == expected


def test_issue_escalation_flag_and_filters(client, db_session):
    from datetime import datetime, timedelta
    from app.models import Issue

    old = Issue(ref="OLD-ISSUE", kind="noise", department="TANGEDCO", message="Old complaint",
                locality="Adyar", pincode="600020", created=datetime.utcnow() - timedelta(days=4))
    db_session.add(old)
    db_session.commit()
    payload = client.get("/api/issues?pincode=600020&department=TANGEDCO").json()
    assert payload[0]["is_escalated"] is True
    assert client.get("/api/issues?pincode=600001").json() == []


@pytest.mark.xfail(strict=True, reason="Known issue: authenticated officers can reply across department boundaries")
def test_officer_must_not_reply_to_another_department_issue(client, db_session, make_project, auth_headers):
    from app.models import Issue

    project = make_project(department="GCC Roads & Bridges")
    issue = Issue(ref="X-DEPT-1", project_id=project.id, kind="noise", department=project.department,
                  message="Problem", locality=project.locality, pincode=project.pincode)
    db_session.add(issue)
    db_session.commit()
    response = client.post(f"/api/issues/{issue.id}/reply", headers=auth_headers, json={"reply": "Reply"})
    assert response.status_code == 403


def test_geocoding_endpoints_and_input_validation(client, monkeypatch):
    from app.routers import geocode

    monkeypatch.setattr(geocode, "resolve_pincode_coordinates", lambda pin: {"locality": "Fake", "lat": 13.0, "lng": 80.0})
    assert client.get("/api/geocode/pincode?pin=600017").json()["locality"] == "Fake"
    assert client.get("/api/geocode/pincode?pin=12").status_code == 400
    reverse = client.get("/api/geocode/reverse?lat=13.04&lng=80.23").json()
    assert reverse["lat"] == 13.04 and reverse["pincode"] == "600001"


def test_conflict_scan_ticket_list_resolution_and_reschedule(client, make_project, make_ticket, auth_headers, token_for):
    project = make_project(department="GCC Roads & Bridges", lat=13.0419, lng=80.2338)
    checked = client.post("/api/projects/check-conflicts", json={
        "start_date": "2026-02-01", "due_date": "2026-11-01", "lat": 13.0418, "lng": 80.2337,
    }, headers=auth_headers)
    assert checked.status_code == 200 and checked.json()["total"] == 1
    ticket_payload = {
        "proposed_title": "Water pipeline", "proposed_start": "2026-03-01", "proposed_end": "2026-05-01",
        "proposed_locality": "T. Nagar", "proposed_pincode": "600017", "reason_for_proceeding": "Urgent",
        "conflicting_dept": "GCC Roads & Bridges", "conflicting_project_title": "Road resurfacing",
        "conflicting_project_id": project.id,
    }
    raised = client.post("/api/conflict-tickets", json=ticket_payload, headers=auth_headers)
    assert raised.status_code == 200
    assert client.get("/api/conflict-tickets", headers=auth_headers).json()
    admin = {"Authorization": f"Bearer {token_for('GCC-ENG-0842', 'admin123', 'Greater Chennai Corporation (Admin)')}"}
    resolved = client.post(f"/api/conflict-tickets/{raised.json()['id']}/resolve", json={
        "approved_dept": "GCC Roads & Bridges", "decision": "Roads proceed"
    }, headers=admin)
    assert resolved.status_code == 200
    assert resolved.json()["status"] == "Resolved"
    ticket = make_ticket(ref="CT-RESCHED-1", conflicting_project_id=project.id)
    # Project is from another department but at a distant PIN, so this does not trigger the current PIN-only guard.
    project.pincode = "600020"
    assert client.post(f"/api/conflict-tickets/{ticket.id}/reschedule", json={
        "new_start_date": "2027-01-01", "new_due_date": "2027-02-01"
    }, headers=auth_headers).status_code == 200


def test_conflict_ticket_requesting_dept_wins_and_new_work_is_created(client, make_project, auth_headers, token_for):
    other = make_project(department="GCC Roads & Bridges", code="ROAD-1")
    ticket = client.post("/api/conflict-tickets", headers=auth_headers, json={
        "proposed_title": "New pipeline", "proposed_start": "2027-01-01", "proposed_end": "2027-03-01",
        "proposed_locality": "T. Nagar", "proposed_pincode": "600017", "reason_for_proceeding": "Critical",
        "conflicting_dept": "GCC Roads & Bridges", "conflicting_project_title": other.title,
        "conflicting_project_id": other.id,
    }).json()
    admin = {"Authorization": f"Bearer {token_for('GCC-ENG-0842', 'admin123', 'Greater Chennai Corporation (Admin)')}"}
    result = client.post(f"/api/conflict-tickets/{ticket['id']}/resolve", headers=admin, json={
        "approved_dept": "Chennai Metro Water", "decision": "Water works have priority",
    })
    assert result.status_code == 200 and result.json()["approved_dept"] == "Chennai Metro Water"
    projects = client.get("/api/projects?search=New%20pipeline").json()
    assert len(projects) == 1 and projects[0]["status"] == "In progress"
    assert client.get("/api/projects/99999").status_code == 404


def test_conflict_ticket_rejects_wrong_role_and_handles_missing_or_unresolved(client, make_ticket):
    field = client.post("/api/auth/login", json={"employee_id": "GCC-FIELD-552", "password": "field123"}).json()["access_token"]
    headers = {"Authorization": f"Bearer {field}"}
    ticket_payload = {
        "proposed_title": "Work", "proposed_start": "2027-01-01", "proposed_end": "2027-02-01",
        "proposed_locality": "Adyar", "reason_for_proceeding": "Urgent",
        "conflicting_dept": "Roads", "conflicting_project_title": "Road work",
    }
    assert client.post("/api/conflict-tickets", headers=headers, json=ticket_payload).status_code == 403
    assert client.post("/api/conflict-tickets/99999/resolve", headers=headers, json={
        "approved_dept": "Roads", "decision": "Proceed",
    }).status_code == 403
    ticket = make_ticket(ref="CT-PENDING", status="Pending", rescheduled_dept="Chennai Metro Water")
    water = client.post("/api/auth/login", json={"employee_id": "CMW-DIV-0219", "password": "water123"}).json()["access_token"]
    water_headers = {"Authorization": f"Bearer {water}"}
    assert client.post(f"/api/conflict-tickets/{ticket.id}/reschedule", headers=water_headers, json={
        "new_start_date": "2027-01-01", "new_due_date": "2027-02-01",
    }).status_code == 400
    assert client.post("/api/conflict-tickets/99999/reschedule", headers=water_headers, json={
        "new_start_date": "2027-01-01", "new_due_date": "2027-02-01",
    }).status_code == 404


def test_conflicting_department_reschedule_and_same_pincode_collision(client, make_project, make_ticket):
    conflicting = make_project(code="RESCHED-ROAD", department="GCC Roads & Bridges", pincode="600017")
    nearby_other = make_project(code="RESCHED-WATER", department="Chennai Metro Water", pincode="600017")
    ticket = make_ticket(ref="CT-ROAD-RESCHED", requesting_dept="Chennai Metro Water",
                         conflicting_project_id=conflicting.id, approved_dept="Chennai Metro Water",
                         rescheduled_dept="GCC Roads & Bridges", proposed_pincode="600017")
    roads = client.post("/api/auth/login", json={"employee_id": "GCC-RD-0155", "password": "roads123"}).json()["access_token"]
    headers = {"Authorization": f"Bearer {roads}"}
    clash = client.post(f"/api/conflict-tickets/{ticket.id}/reschedule", headers=headers, json={
        "new_start_date": "2026-02-01", "new_due_date": "2026-10-01",
    })
    assert clash.status_code == 400
    nearby_other.pincode = "600020"
    moved = client.post(f"/api/conflict-tickets/{ticket.id}/reschedule", headers=headers, json={
        "new_start_date": "2027-01-01", "new_due_date": "2027-02-01",
    })
    assert moved.status_code == 200
    assert conflicting.status == "Scheduled"


def test_digsync_endpoint_is_serializable(client, make_project):
    make_project(code="D1", department="Water")
    make_project(code="D2", department="Roads")
    response = client.get("/api/digsync")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_onsite_projects_submissions_photo_log_blocker_delay_and_review(client, make_project, auth_headers):
    project = make_project()
    assert client.get("/api/onsite/my-projects", headers=auth_headers).status_code == 200
    for kind, fields in [
        ("progress", {"progress_pct": 44, "step_number": 3}),
        ("photo", {"photo_url": "https://example.org/photo.jpg", "photo_caption": "Proof"}),
        ("blocker", {"severity": "High"}),
        ("shift_log", {"labor_count": 8, "machinery_deployed": "JCB", "shift_hours": "Day"}),
        ("delay", {}),
    ]:
        response = client.post("/api/onsite/submissions", headers=auth_headers, json={
            "project_id": project.id, "report_type": kind, "summary": f"{kind} summary", "detail": "Details", **fields
        })
        assert response.status_code == 200, response.text
    submissions = client.get("/api/onsite/submissions", headers=auth_headers).json()
    assert len(submissions) == 5
    assert client.get(f"/api/onsite/submissions?project_id={project.id}", headers=auth_headers).status_code == 200
    review = client.patch(f"/api/onsite/submissions/{submissions[0]['id']}/status", headers=auth_headers, json={"status": "Approved"})
    assert review.status_code == 200 and review.json()["status"] == "Approved"


def test_onsite_department_scoping_and_invalid_project(client, make_project):
    make_project(department="GCC Roads & Bridges", code="R-1")
    make_project(department="Chennai Metro Water", code="W-1")
    field = client.post("/api/auth/login", json={"employee_id": "GCC-FIELD-552", "password": "field123"}).json()["access_token"]
    headers = {"Authorization": f"Bearer {field}"}
    result = client.get("/api/onsite/my-projects", headers=headers).json()
    assert result and all("Roads" in item["department"] for item in result)
    assert client.post("/api/onsite/submissions", headers=headers, json={
        "project_id": 999, "report_type": "progress", "summary": "x", "detail": "y",
    }).status_code == 404
    assert client.get("/api/onsite/submissions").status_code == 401


def test_broadcast_dispatch_and_logs(client, auth_headers):
    payload = {"pincode": "600017", "message": "Road closure tomorrow", "target_count": 17}
    sent = client.post("/api/whatsapp/broadcast", headers=auth_headers, json=payload)
    assert sent.status_code == 200 and sent.json()["recipients_count"] == 17
    assert client.post("/api/broadcasts/whatsapp", headers=auth_headers, json=payload).status_code == 200
    logs = client.get("/api/broadcasts/logs?pincode=600017", headers=auth_headers)
    assert logs.status_code == 200 and len(logs.json()) == 2


@pytest.mark.xfail(strict=True, reason="Known issue: broadcast logs accept any authenticated role")
def test_field_role_must_not_read_broadcast_logs(client):
    token = client.post("/api/auth/login", json={"employee_id": "GCC-FIELD-552", "password": "field123"}).json()["access_token"]
    response = client.get("/api/broadcasts/logs", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403


@pytest.mark.xfail(strict=True, reason="Known issue: reschedule route does not verify ticket department ownership")
def test_officer_must_not_reschedule_ticket_for_other_department(client, make_ticket):
    ticket = make_ticket(ref="CT-OTHER-DEPT", requesting_dept="GCC Roads & Bridges",
                         rescheduled_dept="GCC Roads & Bridges", proposed_pincode="600017")
    water = client.post("/api/auth/login", json={"employee_id": "CMW-DIV-0219", "password": "water123"}).json()["access_token"]
    response = client.post(f"/api/conflict-tickets/{ticket.id}/reschedule", headers={"Authorization": f"Bearer {water}"},
                           json={"new_start_date": "2027-01-01", "new_due_date": "2027-02-01"})
    assert response.status_code == 403


def test_health_and_root_over_http(client):
    assert client.get("/").status_code == 200
    assert client.get("/api/health").json()["status"] == "healthy"
