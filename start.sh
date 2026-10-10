#!/usr/bin/env bash

# Utopia — Smart Public Works Transparency & Municipal Operations Platform
# Unified Launch Script
#
# Usage:
#   ./start.sh            Run in foreground (Ctrl+C stops everything)
#   ./start.sh start      Run in background (survives SSH logout)   [-d | --daemon]
#   ./start.sh stop       Stop background services
#   ./start.sh restart    Stop, then start in background
#   ./start.sh status     Show whether services are running
#   ./start.sh logs       Follow backend + frontend logs

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PATH="$HOME/.local/bin:$HOME/anaconda3/bin:/usr/local/bin:$PATH"

BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"
VENV_DIR="$BACKEND_DIR/venv"
RUN_DIR="$SCRIPT_DIR/.run"
PYTHON_VERSION="${PYTHON_VERSION:-3.12}"
BACKEND_PORT="${PORT:-8001}"
FRONTEND_PORT="${FRONTEND_PORT:-5174}"
export DATABASE_URL="${DATABASE_URL:-sqlite:///$BACKEND_DIR/utopia.db}"

PYTHON_BIN="$VENV_DIR/bin/python"
UVICORN_BIN="$VENV_DIR/bin/uvicorn"

BACKEND_PID_FILE="$RUN_DIR/backend.pid"
FRONTEND_PID_FILE="$RUN_DIR/frontend.pid"
BACKEND_LOG="$RUN_DIR/backend.log"
FRONTEND_LOG="$RUN_DIR/frontend.log"

CMD="${1:-run}"

usage() {
    sed -n '4,11p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
}

# ----------------------------------------------------------------- helpers

pid_alive() {
    local f="$1"
    [ -f "$f" ] && kill -0 "$(cat "$f")" 2>/dev/null
}

free_port() {
    local port="$1" pids=""
    if command -v lsof >/dev/null 2>&1; then
        pids=$(lsof -ti :"$port" 2>/dev/null || true)
    elif command -v fuser >/dev/null 2>&1; then
        pids=$(fuser "$port"/tcp 2>/dev/null || true)
    fi
    if [ -n "$pids" ]; then
        echo "  Freeing port $port (stale PID: $pids)..."
        # shellcheck disable=SC2086
        kill -9 $pids 2>/dev/null || true
        sleep 1
    fi
}

stop_one() {
    local name="$1" pidfile="$2" pid
    if [ -f "$pidfile" ]; then
        pid=$(cat "$pidfile")
        if kill -0 "$pid" 2>/dev/null; then
            echo "  Stopping $name (PID: $pid)..."
            # Services run in their own session, so -PID signals the whole process group
            kill -TERM -- "-$pid" 2>/dev/null || kill -TERM "$pid" 2>/dev/null || true
            for _ in 1 2 3 4 5 6 7 8 9 10; do
                kill -0 "$pid" 2>/dev/null || break
                sleep 0.5
            done
            if kill -0 "$pid" 2>/dev/null; then
                kill -KILL -- "-$pid" 2>/dev/null || kill -KILL "$pid" 2>/dev/null || true
            fi
        fi
        rm -f "$pidfile"
    fi
}

stop_services() {
    stop_one "Frontend" "$FRONTEND_PID_FILE"
    stop_one "Backend" "$BACKEND_PID_FILE"
    # Fallback: anything still holding the ports
    free_port "$BACKEND_PORT"
    free_port "$FRONTEND_PORT"
}

# Public IP lookup (EC2 IMDSv2); falls back to localhost
detect_host_ip() {
    HOST_IP="localhost"
    if command -v curl >/dev/null 2>&1; then
        local token ip
        token=$(curl -s -m 2 -X PUT "http://169.254.169.254/latest/api/token" \
            -H "X-aws-ec2-metadata-token-ttl-seconds: 60" 2>/dev/null || true)
        if [ -n "$token" ]; then
            ip=$(curl -s -m 2 -H "X-aws-ec2-metadata-token: $token" \
                "http://169.254.169.254/latest/meta-data/public-ipv4" 2>/dev/null || true)
            if [[ "$ip" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
                HOST_IP="$ip"
            fi
        fi
    fi
}

print_banner() {
    echo ""
    echo "================================================================="
    echo "  ✅ Utopia Services are Running! ($1)"
    echo "================================================================="
    echo "  🌍 Web Application:      http://$HOST_IP:$FRONTEND_PORT"
    echo "  📡 Backend REST API:     http://$HOST_IP:$BACKEND_PORT"
    echo "  📚 API Documentation:    http://$HOST_IP:$BACKEND_PORT/docs"
    if [ "$HOST_IP" != "localhost" ]; then
        echo "     (open ports $FRONTEND_PORT and $BACKEND_PORT in the EC2 security group,"
        echo "      or use nginx on 80/443)"
    fi
    echo ""
    echo "  🔐 Municipal Portal Login Credentials (/admin):"
    echo "     - GCC Admin:          admin@gcc.gov.in / admin123"
    echo "     - Metro Water:        water@metrowater.tn.gov.in / water123"
    echo "     - Roads & Bridges:    roads@gcc.gov.in / roads123"
    echo "     - Electricity (TNEB): power@tangedco.gov.in / power123"
    echo "     - Field Supervisor:   field.gcc@chennai.gov.in / field123"
    echo "================================================================="
}

prepare_environment() {
    # uv provisions Python $PYTHON_VERSION without touching the system Python
    if ! command -v uv >/dev/null 2>&1; then
        echo "[Setup] uv not found. Installing..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH="$HOME/.local/bin:$PATH"
        if ! command -v uv >/dev/null 2>&1; then
            echo "Error: uv installation failed!" >&2
            exit 1
        fi
    fi

    # Recreate the venv if it was built with a different Python version
    if [ -d "$VENV_DIR" ]; then
        local current
        current=$("$PYTHON_BIN" -c 'import sys; print(f"{sys.version_info[0]}.{sys.version_info[1]}")' 2>/dev/null || echo "none")
        if [ "$current" != "$PYTHON_VERSION" ]; then
            echo "[Backend] Existing venv uses Python $current, need $PYTHON_VERSION. Recreating..."
            rm -rf "$VENV_DIR"
        fi
    fi

    if [ ! -d "$VENV_DIR" ]; then
        echo "[Backend] Creating virtual environment (Python $PYTHON_VERSION) in $VENV_DIR..."
        uv venv --python "$PYTHON_VERSION" "$VENV_DIR"
    fi

    if [ ! -f "$UVICORN_BIN" ]; then
        echo "[Backend] Installing dependencies from requirements.txt..."
        uv pip install --python "$PYTHON_BIN" -r "$BACKEND_DIR/requirements.txt"
    fi

    if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
        echo "[Frontend] Installing dependencies via npm..."
        (cd "$FRONTEND_DIR" && npm install)
    fi
}

print_header() {
    echo "================================================================="
    echo "  🚀 Starting Utopia Platform"
    echo "================================================================="
    echo "  Project Root: $SCRIPT_DIR"
    echo "  Python:       $PYTHON_VERSION (via uv)"
    echo "  Backend Port: $BACKEND_PORT"
    echo "  Frontend Port: $FRONTEND_PORT"
    echo "  Database:     $DATABASE_URL"
    echo "================================================================="
}

# ----------------------------------------------------------------- commands

run_background() {
    mkdir -p "$RUN_DIR"
    print_header
    echo "  Mode:         background (logs in $RUN_DIR)"
    echo "================================================================="

    # Stop any previous background run and clear stale ports
    stop_services
    prepare_environment

    # Auto-reload is for development; off in background unless UVICORN_RELOAD=1
    local reload_flag=""
    [ "${UVICORN_RELOAD:-0}" = "1" ] && reload_flag="--reload"

    echo "[Backend] Starting FastAPI Uvicorn server on port $BACKEND_PORT..."
    (
        cd "$BACKEND_DIR"
        # setsid + nohup: detached from the terminal, immune to SSH hangup
        # shellcheck disable=SC2086
        setsid nohup "$UVICORN_BIN" app.main:app --host 0.0.0.0 --port "$BACKEND_PORT" $reload_flag \
            >"$BACKEND_LOG" 2>&1 </dev/null &
        echo $! >"$BACKEND_PID_FILE"
    )

    sleep 2

    echo "[Frontend] Starting Vite dev server on port $FRONTEND_PORT..."
    (
        cd "$FRONTEND_DIR"
        setsid nohup npm run dev -- --host 0.0.0.0 --port "$FRONTEND_PORT" --strictPort \
            >"$FRONTEND_LOG" 2>&1 </dev/null &
        echo $! >"$FRONTEND_PID_FILE"
    )

    sleep 3

    local failed=0
    if ! pid_alive "$BACKEND_PID_FILE"; then
        echo "❌ Backend failed to start. Last log lines:" >&2
        tail -n 20 "$BACKEND_LOG" >&2 || true
        failed=1
    fi
    if ! pid_alive "$FRONTEND_PID_FILE"; then
        echo "❌ Frontend failed to start. Last log lines:" >&2
        tail -n 20 "$FRONTEND_LOG" >&2 || true
        failed=1
    fi
    if [ "$failed" -eq 1 ]; then
        stop_services
        exit 1
    fi

    detect_host_ip
    print_banner "background"
    echo "  Backend PID:  $(cat "$BACKEND_PID_FILE")"
    echo "  Frontend PID: $(cat "$FRONTEND_PID_FILE")"
    echo "  Logs:         ./start.sh logs"
    echo "  Stop:         ./start.sh stop"
    echo "================================================================="
}

run_foreground() {
    print_header
    free_port "$BACKEND_PORT"
    free_port "$FRONTEND_PORT"
    prepare_environment

    local backend_pid="" frontend_pid=""

    cleanup() {
        trap - INT TERM EXIT
        echo ""
        echo "================================================================="
        echo "  Shutting down Utopia services..."
        echo "================================================================="
        if [ -n "${backend_pid:-}" ] && kill -0 "$backend_pid" 2>/dev/null; then
            echo "  Stopping Backend (PID: $backend_pid)..."
            kill -TERM "$backend_pid" 2>/dev/null || true
        fi
        if [ -n "${frontend_pid:-}" ] && kill -0 "$frontend_pid" 2>/dev/null; then
            echo "  Stopping Frontend (PID: $frontend_pid)..."
            kill -TERM "$frontend_pid" 2>/dev/null || true
        fi
        wait 2>/dev/null || true
        echo "  All services stopped cleanly."
    }
    trap cleanup INT TERM EXIT

    echo "[Backend] Starting FastAPI Uvicorn server on port $BACKEND_PORT..."
    (
        cd "$BACKEND_DIR"
        exec "$UVICORN_BIN" app.main:app --host 0.0.0.0 --port "$BACKEND_PORT" --reload
    ) &
    backend_pid=$!

    sleep 2

    echo "[Frontend] Starting Vite dev server on port $FRONTEND_PORT..."
    (
        cd "$FRONTEND_DIR"
        exec npm run dev -- --host 0.0.0.0 --port "$FRONTEND_PORT" --strictPort
    ) &
    frontend_pid=$!

    detect_host_ip
    print_banner "foreground"
    echo "  Press Ctrl+C to stop all services."
    echo "  (Closing SSH will stop them. Use './start.sh start' to run in background.)"
    echo "================================================================="
    echo ""

    wait "$backend_pid" "$frontend_pid"
}

show_status() {
    local rc=0
    for pair in "Backend:$BACKEND_PID_FILE" "Frontend:$FRONTEND_PID_FILE"; do
        local name="${pair%%:*}" file="${pair#*:}"
        if pid_alive "$file"; then
            echo "  $name: running (PID $(cat "$file"))"
        else
            echo "  $name: not running"
            rc=1
        fi
    done
    return "$rc"
}

# ----------------------------------------------------------------- dispatch

case "$CMD" in
    run|"")                        run_foreground ;;
    start|-d|--daemon|--background) run_background ;;
    stop)                          stop_services; echo "  All services stopped." ;;
    restart)                       run_background ;;
    status)                        show_status ;;
    logs)
        mkdir -p "$RUN_DIR"
        touch "$BACKEND_LOG" "$FRONTEND_LOG"
        exec tail -n 50 -F "$BACKEND_LOG" "$FRONTEND_LOG"
        ;;
    -h|--help|help)                usage ;;
    *)                             echo "Unknown command: $CMD" >&2; usage >&2; exit 1 ;;
esac
