#!/data/data/com.termux/files/usr/bin/bash

BASE="$HOME/APEX-SOVEREIGN-V3/backend"
PIDFILE="$BASE/backend.pid"
LOG="$BASE/logs/backend.log"

cd "$BASE" || exit 1

if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
    echo "APEX Backend already running."
    exit 0
fi

source "$BASE/venv/bin/activate"

nohup uvicorn app.main:app \
    --host 127.0.0.1 \
    --port 8000 \
    >> "$LOG" 2>&1 </dev/null &

echo $! > "$PIDFILE"

sleep 3

if curl -fsS http://127.0.0.1:8000/ >/dev/null; then
    echo "APEX Backend started successfully."
    termux-notification --id 8000 \
        --title "APEX Backend Running" \
        --content "Local API is active" \
        --ongoing 2>/dev/null || true
else
    echo "Backend failed. Check logs:"
    tail -40 "$LOG"
    rm -f "$PIDFILE"
    exit 1
fi
