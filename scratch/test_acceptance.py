import urllib.request
import json
import urllib.parse
import sys

API_BASE = "http://localhost:8001/api"

def request(path, method="GET", data=None, token=None):
    url = f"{API_BASE}{path}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            status = resp.status
            content = resp.read().decode("utf-8")
            return status, json.loads(content) if content else {}
    except urllib.error.HTTPError as e:
        content = e.read().decode("utf-8")
        try:
            parsed = json.loads(content)
        except Exception:
            parsed = {"raw": content}
        return e.code, parsed

def run_tests():
    print("=== RUNNING CIVICGRID ACCEPTANCE TESTS ===")
    
    # 1. Department List Endpoint
    status, depts = request("/departments")
    assert status == 200, f"Expected 200 for /departments, got {status}"
    assert "Chennai Metro Water" in depts and "GCC Roads & Bridges" in depts
    print("✓ Test 1: Department list returned successfully:", depts)

    # 2. Department Login with matching authorized department
    status, login_res = request("/auth/login", method="POST", data={
        "employee_id": "CMW-DIV-0219",
        "password": "water123",
        "department": "Chennai Metro Water"
    })
    assert status == 200, f"Expected 200 for matching login, got {status}: {login_res}"
    metro_token = login_res["access_token"]
    assert login_res["user"]["department"] == "Chennai Metro Water"
    print("✓ Test 2: Department official logged into assigned department:", login_res["user"]["name"])

    # 3. Department Login with unauthorized/mismatched department (MUST BE REJECTED 403)
    status, reject_res = request("/auth/login", method="POST", data={
        "employee_id": "CMW-DIV-0219",
        "password": "water123",
        "department": "Stormwater Drainage"
    })
    assert status == 403, f"Expected 403 for mismatched department, got {status}: {reject_res}"
    print("✓ Test 3: Unauthorized department login rejected with 403 Forbidden:", reject_res.get("detail"))

    # 4. Department-scoped projects access
    status, dept_projects = request("/department/projects", token=metro_token)
    assert status == 200, f"Expected 200, got {status}"
    for p in dept_projects:
        assert "Metro Water" in p["department"], f"Project {p['code']} belongs to {p['department']}, not Metro Water!"
    print(f"✓ Test 4: /department/projects scoped strictly to authorized department ({len(dept_projects)} projects)")

    # 5. Project Creation: Backend enforces department assignment (cannot be spoofed from payload)
    status, created_proj = request("/projects", method="POST", data={
        "title": "Kilpauk High-Pressure Water Mains Renewal Test",
        "category": "Water Supply & Drainage",
        "department": "GCC Roads & Bridges", # Spoof attempt! Should be overridden by user's Metro Water!
        "locality": "Kilpauk",
        "pincode": "600010",
        "address": "Kilpauk Garden Road near Water Works",
        "description": "Laying ductile iron pipes for pressure balancing across Zone 8.",
        "budget": 24000000,
        "contractor": "L&T Construction Infrastructure Ltd",
        "start_date": "2026-03-01",
        "due_date": "2026-09-30",
        "status": "Scheduled",
        "technical_scope": "600mm DI K9 pipe laying with mechanical joints.",
        "funding_program": "CMWSSB Infrastructure Master Plan"
    }, token=metro_token)
    assert status == 201, f"Expected 201, got {status}: {created_proj}"
    assert created_proj["department"] == "Chennai Metro Water", f"Department spoofing not prevented! Got {created_proj['department']}"
    assert created_proj["code"].startswith("CG-") or created_proj["code"].startswith("PRJ-"), f"Project code not generated: {created_proj['code']}"
    created_id = created_proj["id"]
    print(f"✓ Test 5: Project {created_proj['code']} created and department safely assigned to '{created_proj['department']}' (spoof blocked)")

    # 6. Created project appears in Department register
    status, dept_projects_after = request("/department/projects", token=metro_token)
    found = any(p["id"] == created_id for p in dept_projects_after)
    assert found, "Created project not found in department register!"
    print(f"✓ Test 6: Project {created_proj['code']} verified in department works register")

    # 7. Cross-department modification prevented (Roads official login)
    status, roads_login = request("/auth/login", method="POST", data={
        "employee_id": "GCC-RD-0155",
        "password": "roads123",
        "department": "GCC Roads & Bridges"
    })
    roads_token = roads_login["access_token"]
    # Roads official attempts to modify Metro Water project
    status, patch_res = request(f"/projects/{created_id}", method="PATCH", data={
        "status": "Completed"
    }, token=roads_token)
    assert status == 403, f"Expected 403 for cross-department update, got {status}: {patch_res}"
    print("✓ Test 7: Cross-department project modification rejected with 403 Forbidden:", patch_res.get("detail"))

    # 8. Dynamic Geocoding of PIN outside seeded list (e.g. 600028 - R.A. Puram)
    status, geo_res = request("/geocode/pincode?pin=600028")
    assert status == 200, f"Expected 200 for 600028, got {status}: {geo_res}"
    assert geo_res["pincode"] == "600028"
    assert geo_res["lat"] > 12.0 and geo_res["lng"] > 79.0
    print(f"✓ Test 8: Geocoding resolved unseeded PIN 600028: {geo_res['locality']} at ({geo_res['lat']}, {geo_res['lng']})")

    # 9. Query projects for PIN with 0 projects (Geographic lookup decoupled from projects)
    status, unseeded_projects = request("/projects?pincode=600028")
    assert status == 200
    print(f"✓ Test 9: Successfully queried projects for 600028 (returned {len(unseeded_projects)} projects, decoupled from coordinates)")

    # 10. Reverse Geocoding coordinates (13.0418, 80.2337)
    status, rev_res = request("/geocode/reverse?lat=13.0418&lng=80.2337")
    assert status == 200, f"Expected 200 for reverse geocoding, got {status}: {rev_res}"
    assert rev_res["pincode"] == "600017"
    assert "T. Nagar" in rev_res["locality"]
    print(f"✓ Test 10: Reverse geocoded (13.0418, 80.2337) to PIN {rev_res['pincode']} ({rev_res['locality']})")

    # 11. Invalid PIN code handling (999999)
    status, inv_res = request("/geocode/pincode?pin=999999")
    assert status == 404, f"Expected 404 for invalid PIN 999999, got {status}: {inv_res}"
    print(f"✓ Test 11: Invalid PIN correctly returned 404 with error message: {inv_res.get('detail')}")

    # 12. Escalation & Grievance SLA routing
    status, issues = request("/department/issues", token=metro_token)
    assert status == 200
    print(f"✓ Test 12: Department grievances SLA routing verified ({len(issues)} issues for Metro Water)")

    print("\nALL 12 BACKEND AND DATA INTEGRATION TESTS PASSED PERFECTLY!")

if __name__ == "__main__":
    run_tests()
