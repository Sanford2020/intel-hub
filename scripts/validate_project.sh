#!/usr/bin/env bash
# Intel Hub - one-shot project validation (Linux/macOS bash)

set +e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKIP_DOCKER=0
SKIP_FRONTEND=0
SKIP_BACKEND=0
QUICK=0
PASSED=()
FAILED=()

usage() {
  cat <<'EOF'
Usage: bash scripts/validate_project.sh [options]

Options:
  --skip-docker     Skip docker compose config
  --skip-backend    Skip backend pytest
  --skip-frontend   Skip frontend type-check and build
  --quick           Skip frontend production build
  -h, --help        Show this help
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --skip-docker)
      SKIP_DOCKER=1
      ;;
    --skip-backend)
      SKIP_BACKEND=1
      ;;
    --skip-frontend)
      SKIP_FRONTEND=1
      ;;
    --quick)
      QUICK=1
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "[args] FAIL - unknown option: $1"
      usage
      exit 2
      ;;
  esac
  shift
done

write_step() {
  printf '[%s] %s\n' "$1" "$2"
}

command_exists() {
  command -v "$1" >/dev/null 2>&1
}

run_step() {
  local label="$1"
  shift

  write_step "$label" "running..."
  ( "$@" )
  local status=$?

  if [[ $status -eq 0 ]]; then
    PASSED+=("$label")
    write_step "$label" "PASS"
  else
    FAILED+=("$label: exit code $status")
    write_step "$label" "FAIL - exit code $status"
  fi
}

echo "=== Intel Hub validate_project ==="
echo "Root: $ROOT"
echo ""

if [[ $SKIP_DOCKER -eq 0 ]]; then
  if ! command_exists docker; then
    FAILED+=("docker: command not found (use --skip-docker to ignore)")
    write_step "docker" "FAIL - docker not found"
  else
    run_step "docker-config" bash -lc "cd '$ROOT' && docker compose config >/dev/null"
  fi
else
  write_step "docker" "SKIPPED"
fi

if [[ $SKIP_BACKEND -eq 0 ]]; then
  if [[ -n "${PYTHON:-}" ]]; then
    PYTHON_BIN="$PYTHON"
  elif command_exists python; then
    PYTHON_BIN="python"
  elif command_exists python3; then
    PYTHON_BIN="python3"
  else
    PYTHON_BIN=""
  fi

  if [[ -z "$PYTHON_BIN" ]]; then
    FAILED+=("backend: python not found")
    write_step "backend" "FAIL - python not found"
  else
    run_step "backend-pytest" bash -lc "cd '$ROOT/backend' && PYTHONPATH='$ROOT' '$PYTHON_BIN' -m pytest tests/ -q"
  fi
else
  write_step "backend" "SKIPPED"
fi

if [[ $SKIP_FRONTEND -eq 0 ]]; then
  if ! command_exists npm; then
    FAILED+=("frontend: npm not found")
    write_step "frontend" "FAIL - npm not found"
  else
    run_step "frontend-type-check" bash -lc "cd '$ROOT/apps/web' && npm run type-check"
    if [[ $QUICK -eq 0 ]]; then
      run_step "frontend-build" bash -lc "cd '$ROOT/apps/web' && npm run build"
    else
      write_step "frontend-build" "SKIPPED (--quick)"
    fi
  fi
else
  write_step "frontend" "SKIPPED"
fi

echo ""
echo "=== Summary ==="
echo "PASSED (${#PASSED[@]}): ${PASSED[*]}"

if [[ ${#FAILED[@]} -gt 0 ]]; then
  echo "FAILED (${#FAILED[@]}):"
  for item in "${FAILED[@]}"; do
    echo "  - $item"
  done
  exit 1
fi

echo "All checks passed."
exit 0
