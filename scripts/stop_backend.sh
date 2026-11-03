#!/data/data/com.termux/files/usr/bin/bash

BASE="$HOME/APEX-SOVEREIGN-V3/backend"
PIDFILE="$BASE/backend.pid"

if [ -f "$PIDFILE" ]; then
    PID="$(cat "$PIDFILE")"

    if kill -0 "$PID" 2>/dev/null; then
        kill "$PID"
        echo "APEX Backend stopped."
    fi

    rm -f "$PIDFILE"
fi

termux-notification-remove 8000 2>/dev/null || true
