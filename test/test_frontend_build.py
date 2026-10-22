"""Compile-time smoke coverage for the React/TypeScript frontend."""
from pathlib import Path
import shutil
import subprocess

import pytest

FRONTEND = Path(__file__).resolve().parents[1] / "frontend"


@pytest.mark.skipif(
    shutil.which("npm") is None or not (FRONTEND / "node_modules").exists(),
    reason="Run npm ci in frontend/ before the frontend build check",
)
def test_frontend_typescript_and_production_bundle():
    result = subprocess.run(
        ["npm", "run", "build"], cwd=FRONTEND, capture_output=True, text=True
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert (FRONTEND / "dist/index.html").exists()
