#!/usr/bin/env bash
# One command: fetch media if missing, then play. Extra args go to badapple.py.
cd "$(dirname "$0")"
[ -f media/bad_apple.mp4 ] || ./download.sh || exit 1
exec python3 badapple.py "$@"
