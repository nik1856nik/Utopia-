"""Black-box smoke checks against the running Compose stack (stdlib only)."""
import json
import os
import sys
import time
from urllib.parse import quote
from pathlib import Path
import tempfile
import urllib.request
from uuid import uuid4

BASE = os.environ.get("UTOPIA_BASE_URL", "http://localhost:5174").rstrip("/")
MARKER = Path(tempfile.gettempdir()) / "utopia-compose-smoke-title.txt"


def request(path, method="GET", payload=None, token=None):
    headers = {}
    if payload is not None:
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(BASE + path, data=body, method=method, headers=headers)
    with urllib.request.urlopen(req, timeout=8) as response:
        raw = response.read()
        content_type = response.headers.get("content-type", "")
        return response.status, raw, content_type


def wait_until_ready():
    last_error = None
    for _ in range(40):
        try:
            request("/api/health")
            return
        except Exception as error:
            last_error = error
            time.sleep(2)
    raise RuntimeError(f"Compose web/API did not become ready: {last_error}")


def main():
    wait_until_ready()

    status, html, kind = request("/")
    assert status == 200 and "text/html" in kind and b"<div id=\"root\"" in html
    status, html, _ = request("/citizen")
    assert status == 200 and b"<div id=\"root\"" in html, "Nginx SPA fallback failed"

    status, health, _ = request("/api/health")
    assert status == 200 and json.loads(health)["status"] == "healthy", "Nginx API proxy failed"
    status, docs, _ = request("/docs")
    assert status == 200 and b"swagger" in docs.lower(), "Nginx docs proxy failed"
    status, schema, _ = request("/openapi.json")
    api_schema = json.loads(schema)
    assert status == 200 and "/api/projects" in api_schema["paths"], "OpenAPI proxy failed"
    status, projects, _ = request("/api/projects")
    assert status == 200 and isinstance(json.loads(projects), list)

    # Verify DB-backed write/read through Nginx, then restart database and API
    # containers without deleting pgdata to prove the named volume persists.
    status, login, _ = request("/api/auth/login", "POST", {
        "employee_id": "admin@gcc.gov.in", "password": "admin123",
    })
    token = json.loads(login)["access_token"]
    title = f"Compose persistence smoke {uuid4()}"
    MARKER.write_text(title)
    payload = {
        "title": title, "category": "Test", "locality": "T. Nagar", "pincode": "600017",
        "description": "Temporary smoke test record", "budget": 1,
        "start_date": "2027-01-01", "due_date": "2027-02-01",
    }
    created_status, _, _ = request("/api/projects", "POST", payload, token)
    assert created_status == 200, f"API write returned HTTP {created_status}"
    assert any(row["title"] == title for row in json.loads(request("/api/projects?search=" + quote(title))[1]))
    print("PASS: Nginx SPA fallback, API/docs/OpenAPI proxy, API response, and DB write/read.")
    print("PASS: DB persistence across restart must be completed with the command below:")
    print("  docker compose -f compose.yml restart db api")
    print("  python test/compose_smoke.py --verify-persistence")


def verify_persistence():
    if not MARKER.exists():
        raise RuntimeError("Run python test/compose_smoke.py before the restart check")
    wait_until_ready()
    title = MARKER.read_text()
    status, rows, _ = request("/api/projects?search=" + quote(title))
    assert status == 200 and any(row["title"] == title for row in json.loads(rows)), "Smoke record did not survive the restart"
    MARKER.unlink()
    print("PASS: smoke test record survived database/API container restart.")


if __name__ == "__main__":
    if "--verify-persistence" in sys.argv:
        verify_persistence()
    else:
        main()
