#!/usr/bin/env bash

# Utopia — Smart Public Works Transparency & Municipal Operations Platform
# Unified Launch Script

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PATH="$HOME/.local/bin:$HOME/anaconda3/bin:/usr/local/bin:$PATH"

BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"
VENV_DIR="$BACKEND_DIR/venv"
BACKEND_PORT="${PORT:-8001}"
FRONTEND_PORT="${FRONTEND_PORT:-5174}"
export DATABASE_URL="${DATABASE_URL:-sqlite:///$BACKEND_DIR/utopia.db}"

echo "================================================================="
echo "  🚀 Starting Utopia Platform"
echo "================================================================="
echo "  Project Root: $SCRIPT_DIR"
echo "  Backend Port: $BACKEND_PORT"
echo "  Frontend Port: $FRONTEND_PORT"
echo "  Database:     $DATABASE_URL"
echo "================================================================="

# Free up ports if already in use by a previous run
for port in "$BACKEND_PORT" "$FRONTEND_PORT"; do
    PIDS=$(lsof -ti :"$port" 2>/dev/null || true)
    if [ -n "$PIDS" ]; then
        echo "  Freeing port $port (stale PID: $PIDS)..."
        kill -9 $PIDS 2>/dev/null || true
        sleep 1
    fi
done

# 1. Check & Prepare Backend Python Environment
if [ ! -d "$VENV_DIR" ]; then
    echo "[Backend] Virtual environment not found. Creating in $VENV_DIR..."
    if command -v virtualenv >/dev/null 2>&1; then
        virtualenv "$VENV_DIR"
    elif command -v python3 >/dev/null 2>&1; then
        python3 -m venv "$VENV_DIR" || virtualenv "$VENV_DIR"
    else
        echo "Error: Python 3 or virtualenv not found!" >&2
        exit 1
    fi
fi

PYTHON_BIN="$VENV_DIR/bin/python"
PIP_BIN="$VENV_DIR/bin/pip"
UVICORN_BIN="$VENV_DIR/bin/uvicorn"

if [ ! -f "$UVICORN_BIN" ]; then
    echo "[Backend] Installing dependencies from requirements.txt..."
    "$PIP_BIN" install -r "$BACKEND_DIR/requirements.txt"
fi

# 2. Check & Prepare Frontend Environment
if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
    echo "[Frontend] Installing dependencies via npm..."
    (cd "$FRONTEND_DIR" && npm install)
fi

# Process tracking and cleanup trap
BACKEND_PID=""
FRONTEND_PID=""

cleanup() {
    trap - INT TERM EXIT
    echo ""
    echo "================================================================="
    echo "  Shutting down Utopia services..."
    echo "================================================================="
    if [ -n "${BACKEND_PID:-}" ] && kill -0 "$BACKEND_PID" 2>/dev/null; then
        echo "  Stopping Backend (PID: $BACKEND_PID)..."
        kill -TERM "$BACKEND_PID" 2>/dev/null || true
    fi
    if [ -n "${FRONTEND_PID:-}" ] && kill -0 "$FRONTEND_PID" 2>/dev/null; then
        echo "  Stopping Frontend (PID: $FRONTEND_PID)..."
        kill -TERM "$FRONTEND_PID" 2>/dev/null || true
    fi
    wait 2>/dev/null || true
    echo "  All services stopped cleanly."
}

trap cleanup INT TERM EXIT

# 3. Start Backend Service
echo "[Backend] Starting FastAPI Uvicorn server on port $BACKEND_PORT..."
(
    cd "$BACKEND_DIR"
    exec "$UVICORN_BIN" app.main:app --host 0.0.0.0 --port "$BACKEND_PORT" --reload
) &
BACKEND_PID=$!

# Wait briefly to let backend bind
sleep 2

# 4. Start Frontend Service
echo "[Frontend] Starting Vite dev server on port $FRONTEND_PORT..."
(
    cd "$FRONTEND_DIR"
    exec npm run dev
) &
FRONTEND_PID=$!

echo ""
echo "================================================================="
echo "  ✅ Utopia Services are Running!"
echo "================================================================="
echo "  🌍 Web Application:      http://localhost:5174"
echo "  📡 Backend REST API:     http://localhost:$BACKEND_PORT"
echo "  📚 API Documentation:    http://localhost:$BACKEND_PORT/docs"
echo ""
echo "  🔐 Municipal Portal Login Credentials (/admin):"
echo "     - GCC Admin:          admin@gcc.gov.in / admin123"
echo "     - Metro Water:        water@metrowater.tn.gov.in / water123"
echo "     - Roads & Bridges:    roads@gcc.gov.in / roads123"
echo "     - Electricity (TNEB): power@tangedco.gov.in / power123"
echo "     - Field Supervisor:   field.gcc@chennai.gov.in / field123"
echo "================================================================="
echo "  Press Ctrl+C to stop all services."
echo "================================================================="
echo ""

# Keep running until interrupted
wait "$BACKEND_PID" "$FRONTEND_PID"
