#!/bin/sh
# macOS users: double-click this file in Finder.

cd "$(dirname "$0")" || exit 1
exec sh ./start-mac.command "$@"
