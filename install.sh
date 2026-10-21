#!/data/data/com.termux/files/usr/bin/bash
# Installs everything Bad Apple needs on Termux.
set -e

if command -v pkg >/dev/null 2>&1; then
  pkg update -y
  pkg install -y python ffmpeg mpv yt-dlp
else
  echo "pkg not found - not Termux? Install python3, ffmpeg, mpv and yt-dlp manually."
  exit 1
fi

chmod +x badapple.py download.sh run.sh 2>/dev/null || true
echo "Done. Next: ./run.sh"
