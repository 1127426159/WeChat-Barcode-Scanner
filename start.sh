#!/bin/sh
# Start the host. On first run this creates .venv and installs dependencies.
set -e
cd "$(dirname "$0")" || exit 1
. ./setup_env.sh
ensure_env
exec "$PY" -m host "$@"