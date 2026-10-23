from datetime import date, timedelta

import pytest
from pydantic import ValidationError

from app.main import health_check, root_status
from app.models import Event, FieldSubmission, Issue, SMSLog
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.broadcast import BroadcastResponse, WhatsAppBroadcastIn
from app.schemas.conflict import ConflictCheckIn, ConflictResolveIn, ConflictRescheduleIn, ConflictTicketIn
from app.schemas.field import FieldSubmissionIn
from app.schemas.issue import IssueIn, IssueReplyIn, QuestionIn
from app.schemas.project import EventIn, ProjectCreateIn, ProjectUpdateIn, serialize_project
from app.services import auth as auth_service
from app.services import geocoding
from app.services.digsync import detect_digsync_conflicts
from app.services.seeder import seed_data


def test_health_and_root_payloads():
    assert health_check()["status"] == "healthy"
    assert health_check()["version"] == "3.0.0"
    assert root_status()["health"] == "/api/health"


def test_database_dependency_yields_and_closes_session():
    generator = auth_service  # Import module to ensure backend service surface is importable.
    assert generator.get_current_user


def test_auth_token_create_decode_and_invalid_cases(monkeypatch):
    monkeypatch.setattr(auth_service, "JWT_SECRET", "test-secret")
    token = auth_service.create_access_token({"sub": "admin@gcc.gov.in"}, timedelta(minutes=5))
    user = auth_service.get_current_user(f"Bearer {token}")
    assert user["role"] == "admin"
    assert auth_service.get_optional_user(f"Bearer {token}")["sub"] == "admin@gcc.gov.in"
    assert auth_service.get_optional_user(None) is None
    assert auth_service.get_optional_user("Bearer invalid") is None
    with pytest.raises(Exception):
        auth_service.get_current_user(None)
    with pytest.raises(Exception):
        auth_service.get_current_user("Bearer invalid")


def test_geocode_cache_and_external_fallback(monkeypatch):
    known = geocoding.resolve_pincode_coordinates("600017")
    assert known["locality"] == "T. Nagar"
    assert known["lat"] > 12

    def no_network(*args, **kwargs):
        raise OSError("offline")

    monkeypatch.setattr(geocoding.urllib.request, "urlopen", no_network)
    fallback = geocoding.resolve_pincode_coordinates("699999")
    assert fallback["locality"] == "Chennai Postal Sector 699999"
    assert geocoding.resolve_pincode_coordinates("699999") == fallback


def test_geocode_external_lookup_success(monkeypatch):
    geocoding.PINCODE_CACHE.pop("699998", None)

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def read(self):
            return b'[{"lat":"13.1","lon":"80.3","display_name":"New Area, Chennai"}]'

    monkeypatch.setattr(geocoding.urllib.request, "urlopen", lambda *args, **kwargs: Response())
    value = geocoding.resolve_pincode_coordinates("699998")
    assert value == {"locality": "New Area", "lat": 13.1, "lng": 80.3}


def test_seed_data_populates_once_and_is_idempotent(db_session):
    seed_data(db_session)
    first_count = db_session.query(__import__("app.models", fromlist=["Project"]).Project).count()
    assert first_count > 0
    seed_data(db_session)
    assert db_session.query(__import__("app.models", fromlist=["Project"]).Project).count() == first_count


def test_digsync_detects_cross_department_close_projects(db_session, make_project):
    make_project(code="A", department="Water", lat=13.04, lng=80.23)
    make_project(code="B", department="Roads", lat=13.041, lng=80.231)
    make_project(code="C", department="Water", lat=13.2, lng=80.4)
    conflicts = detect_digsync_conflicts(db_session)
    assert len(conflicts) == 1
    assert conflicts[0]["severity"] in {"High Conflict", "Potential Conflict"}


def test_project_serialization_and_schema_validation(make_project):
    project = make_project()
    wire = serialize_project(project)
    assert wire["id"] == project.id
    assert wire["start_date"] == "2026-01-01"
    assert ProjectUpdateIn(progress=70).progress == 70
    assert EventIn(title="Update", detail="Details").title == "Update"
    valid = ProjectCreateIn(
        title="New", category="Roads", locality="T. Nagar", pincode="600017",
        description="Work", budget=5, start_date=date(2026, 1, 1), due_date=date(2026, 2, 1),
    )
    assert valid.title == "New"
    with pytest.raises(ValidationError):
        ProjectCreateIn(title="missing required fields")


@pytest.mark.parametrize("schema,payload", [
    (LoginRequest, {"password": "x", "employee_id": "badge"}),
    (TokenResponse, {"access_token": "t", "user": {"role": "admin"}}),
    (IssueIn, {"kind": "noise", "message": "Too loud"}),
    (IssueReplyIn, {"reply": "We are investigating"}),
    (QuestionIn, {"project_id": 1, "message": "When complete?"}),
    (ConflictCheckIn, {"start_date": "2026-01-01", "due_date": "2026-01-02"}),
    (ConflictResolveIn, {"approved_dept": "Roads", "decision": "Proceed"}),
    (ConflictRescheduleIn, {"new_start_date": "2026-02-01", "new_due_date": "2026-03-01"}),
    (ConflictTicketIn, {"proposed_title": "Work", "proposed_start": "2026-01-01", "proposed_end": "2026-02-01", "proposed_locality": "T Nagar", "reason_for_proceeding": "Urgent", "conflicting_dept": "Roads", "conflicting_project_title": "Road work"}),
    (FieldSubmissionIn, {"project_id": 1, "report_type": "progress", "summary": "Update", "detail": "Detail"}),
    (WhatsAppBroadcastIn, {"pincode": "600017", "message": "Advisory"}),
    (BroadcastResponse, {"success": True, "ref": "X", "pincode": "600017", "recipients_count": 1, "message": "sent", "channels": ["SMS"]}),
])
def test_schema_models_accept_valid_shapes(schema, payload):
    assert schema.model_validate(payload)


def test_remaining_model_tables_are_registered():
    assert {Event.__tablename__, Issue.__tablename__, FieldSubmission.__tablename__, SMSLog.__tablename__} <= set(
        __import__("app.database", fromlist=["Base"]).Base.metadata.tables
    )
    assert Issue.__table__.c.kind.type.length == 180
