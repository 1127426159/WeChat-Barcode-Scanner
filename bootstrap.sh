#!/bin/sh
# One-time setup: creates .venv and installs dependencies.
set -e
cd "$(dirname "$0")" || exit 1
. ./setup_env.sh
ensure_env
printf '\nSetup finished. Run ./start.sh to launch.\n'