#!/bin/bash
# Persistent hourly runner for ignite_collect.py.
# cron is not available on this box (package not installed; no systemd), so this
# loop is the scheduler. It survives agent turn changes as long as the box
# process is not killed; it does not survive a box reboot — start it again with:
#   /workspace/m365ai/scripts/ignite_collect_loop.sh --daemon
set -euo pipefail
ROOT="${TR_IGNITE_DIR:-/workspace/m365ai-ignite}"
SCRIPT="/workspace/m365ai/scripts/ignite_collect.py"
PY="${PYTHON:-python3}"
LOG="$ROOT/collect-loop.log"
PIDFILE="$ROOT/collect-loop.pid"
INTERVAL="${TR_IGNITE_INTERVAL:-3600}"

mkdir -p "$ROOT"

if [[ "${1:-}" == "--status" ]]; then
  if [[ -f "$PIDFILE" ]] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
    echo "running pid=$(cat "$PIDFILE") interval=${INTERVAL}s log=$LOG"
    exit 0
  fi
  echo "not running"
  exit 1
fi

if [[ "${1:-}" == "--stop" ]]; then
  if [[ -f "$PIDFILE" ]] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
    kill "$(cat "$PIDFILE")"
    echo "stopped $(cat "$PIDFILE")"
    rm -f "$PIDFILE"
    exit 0
  fi
  echo "not running"
  exit 1
fi

start_loop() {
  if [[ -f "$PIDFILE" ]] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
    echo "already running pid=$(cat "$PIDFILE")"
    exit 0
  fi
  nohup bash "$0" --foreground >>"$LOG" 2>&1 &
  echo $! > "$PIDFILE"
  disown || true
  echo "started pid=$(cat "$PIDFILE") log=$LOG"
}

if [[ "${1:-}" == "--daemon" || "${1:-}" == "" ]]; then
  start_loop
  exit 0
fi

if [[ "${1:-}" != "--foreground" ]]; then
  echo "usage: $0 [--daemon|--foreground|--status|--stop]"
  exit 2
fi

echo "$$" > "$PIDFILE"
echo "$(date '+%Y-%m-%d %H:%M:%S %Z') loop start pid=$$ interval=${INTERVAL}s"

# Run immediately, then sleep until the next interval. If a run overlaps the
# interval, skip the sleep remainder rather than stacking processes (flock).
LOCK="$ROOT/collect.lock"
while true; do
  start=$(date +%s)
  echo "$(date '+%Y-%m-%d %H:%M:%S %Z') collect begin"
  if command -v flock >/dev/null 2>&1; then
    flock -n "$LOCK" "$PY" "$SCRIPT" || echo "$(date '+%Y-%m-%d %H:%M:%S %Z') collect skipped (lock) or failed: $?"
  else
    "$PY" "$SCRIPT" || echo "$(date '+%Y-%m-%d %H:%M:%S %Z') collect failed: $?"
  fi
  echo "$(date '+%Y-%m-%d %H:%M:%S %Z') collect end"
  now=$(date +%s)
  sleep_for=$(( INTERVAL - (now - start) ))
  if (( sleep_for < 5 )); then
    sleep_for=5
  fi
  sleep "$sleep_for"
done
