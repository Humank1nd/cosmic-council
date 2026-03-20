#!/usr/bin/env bash

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# shellcheck disable=SC1091
. "$ROOT/scripts/ai_stack_env.sh"

MODE="${1:-api}"

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "missing required command: $1" >&2
    exit 1
  fi
}

wait_for_http() {
  local url="$1"
  local label="$2"
  local attempts="${3:-30}"
  local i
  for ((i = 1; i <= attempts; i++)); do
    if curl -fsS "$url" >/dev/null 2>&1; then
      echo "[$label] ready at $url"
      return 0
    fi
    sleep 1
  done
  echo "[$label] did not become ready: $url" >&2
  return 1
}

root_api_attempts() {
  printf '%s\n' "${DREAM_CAESAR_API_READY_ATTEMPTS:-90}"
}

cronus_api_attempts() {
  printf '%s\n' "${CRONUS_API_READY_ATTEMPTS:-45}"
}

ensure_ollama() {
  require_cmd ollama
  if ! ollama list >/dev/null 2>&1; then
    echo "[ollama] local Ollama is not reachable" >&2
    exit 1
  fi
}

run_root_api() {
  require_cmd curl
  ensure_ollama
  cd "$ROOT"
  echo "[dream-caesar] starting API on $API_HOST:$API_PORT"
  "$ROOT/.venv/bin/python" run_server.py &
  ROOT_API_PID=$!
  trap 'kill $ROOT_API_PID 2>/dev/null || true' EXIT INT TERM
  wait_for_http "http://$API_HOST:$API_PORT/health" "dream-caesar" "$(root_api_attempts)"
  wait "$ROOT_API_PID"
}

run_cronus_api() {
  require_cmd curl
  ensure_ollama
  cd "$ROOT/CRONUS"
  echo "[cronus] starting API on $CRONUS_API_HOST:$CRONUS_API_PORT"
  API_PORT="$CRONUS_API_PORT" "$ROOT/CRONUS/.venv/bin/python" -m uvicorn api.main:app --host "$CRONUS_API_HOST" --port "$CRONUS_API_PORT" &
  CRONUS_PID=$!
  trap 'kill $CRONUS_PID 2>/dev/null || true' EXIT INT TERM
  wait_for_http "http://$CRONUS_API_HOST:$CRONUS_API_PORT/health" "cronus" "$(cronus_api_attempts)"
  wait "$CRONUS_PID"
}

run_dual() {
  require_cmd curl
  ensure_ollama
  cd "$ROOT"
  echo "[dream-caesar] starting API on $API_HOST:$API_PORT"
  "$ROOT/.venv/bin/python" run_server.py &
  ROOT_API_PID=$!
  echo "[cronus] starting API on $CRONUS_API_HOST:$CRONUS_API_PORT"
  (
    cd "$ROOT/CRONUS"
    API_PORT="$CRONUS_API_PORT" "$ROOT/CRONUS/.venv/bin/python" -m uvicorn api.main:app --host "$CRONUS_API_HOST" --port "$CRONUS_API_PORT"
  ) &
  CRONUS_PID=$!
  trap 'kill $ROOT_API_PID $CRONUS_PID 2>/dev/null || true' EXIT INT TERM
  wait_for_http "http://$API_HOST:$API_PORT/health" "dream-caesar" "$(root_api_attempts)"
  wait_for_http "http://$CRONUS_API_HOST:$CRONUS_API_PORT/health" "cronus" "$(cronus_api_attempts)"
  wait
}

print_status() {
  require_cmd curl
  ensure_ollama
  echo "Dream Caesar root: $ROOT"
  echo "Runtime root: $DREAM_CAESAR_RUNTIME_ROOT"
  echo "Dream Caesar API: http://$API_HOST:$API_PORT"
  echo "CRONUS API: http://$CRONUS_API_HOST:$CRONUS_API_PORT"
  echo "Ollama model: $OLLAMA_MODEL"
  echo "Ollama base URL: $OLLAMA_BASE_URL"
  echo "---"
  ollama list
}

case "$MODE" in
  api)
    run_root_api
    ;;
  cronus)
    run_cronus_api
    ;;
  dual)
    run_dual
    ;;
  status)
    print_status
    ;;
  *)
    echo "usage: $0 {api|cronus|dual|status}" >&2
    exit 1
    ;;
esac
