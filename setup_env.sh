#!/bin/sh
# Shared bootstrap: ensure .venv exists with dependencies installed.
# Sourced by start.sh and bootstrap.sh.
set -e
cd "$(dirname "$0")" || exit 1

VENV=".venv"
PY="$VENV/bin/python"
PIP_INDEX="https://pypi.tuna.tsinghua.edu.cn/simple"

find_python() {
    for candidate in \
        /Library/Frameworks/Python.framework/Versions/3.13/bin/python3 \
        /Library/Frameworks/Python.framework/Versions/3.12/bin/python3 \
        /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
        /usr/local/bin/python3.13 \
        /usr/local/bin/python3.12 \
        /usr/local/bin/python3.11 \
        python3 python3.12 python3.11 python3.10 python3.9 python3.8 python3.7 python
    do
        if [ -x "$candidate" ]; then
            program="$candidate"
        else
            program="$(command -v "$candidate" 2>/dev/null || true)"
        fi
        if [ -n "$program" ] && "$program" -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 7) else 1)" 2>/dev/null; then
            echo "$program"
            return 0
        fi
    done
    return 1
}

install_python_macos() {
    package_url="https://www.python.org/ftp/python/3.11.9/python-3.11.9-macos11.pkg"
    package_file="$(mktemp "${TMPDIR:-/tmp}/scanner-python.XXXXXX")"
    echo "[0/3] Python 3.7+ was not found. Downloading the official installer..." >&2
    if ! curl -fL --retry 3 --connect-timeout 20 --max-time 600 \
        -o "$package_file" "$package_url"; then
        rm -f "$package_file"
        echo "Failed to download Python from python.org." >&2
        return 1
    fi
    echo "macOS will ask for your administrator password to install Python." >&2
    if ! sudo installer -pkg "$package_file" -target /; then
        rm -f "$package_file"
        echo "Python installation failed." >&2
        return 1
    fi
    rm -f "$package_file"
    return 0
}

ensure_env() {
    if [ -x "$PY" ]; then
        if ! "$PY" -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 7) else 1)" 2>/dev/null; then
            echo "The existing .venv uses Python older than 3.7." >&2
            echo "Delete .venv and run this launcher again." >&2
            exit 1
        fi
    fi

    if [ ! -x "$PY" ]; then
        BASE_PY="$(find_python)" || {
            install_python_macos || exit 1
            BASE_PY="$(find_python)" || {
                echo "Python was installed, but python3 could not be found." >&2
                echo "Open a new Terminal window and run this launcher again." >&2
                exit 1
            }
        }
        echo "[1/3] Creating virtual environment with $BASE_PY ..." >&2
        "$BASE_PY" -m venv "$VENV"
    fi

    if ! "$PY" -c "import pyautogui" >/dev/null 2>&1; then
        echo "[2/3] Installing required dependencies ..." >&2
        "$PY" -m pip install --disable-pip-version-check --timeout 20 --retries 2 \
            -i "$PIP_INDEX" -r requirements.txt
    fi

    if ! "$PY" -c "import segno" >/dev/null 2>&1; then
        echo "[3/3] Installing optional QR support ..." >&2
        # Optional: never block startup when offline.
        "$PY" -m pip install --disable-pip-version-check --timeout 15 --retries 1 \
            -i "$PIP_INDEX" segno >/dev/null 2>&1 \
            || echo "      Skipped: QR support unavailable, text output will be used." >&2
    fi
}
