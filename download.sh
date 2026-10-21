#!/usr/bin/env bash
# Downloads Bad Apple!! and extracts its audio into ./media
# Override the source with: ./download.sh "https://..."
set -e
cd "$(dirname "$0")"

URL="${1:-https://www.youtube.com/watch?v=FtutLA63Cp8}"
mkdir -p media

if [ ! -f media/bad_apple.mp4 ]; then
  yt-dlp -f "bv*[height<=360][ext=mp4]+ba[ext=m4a]/b[height<=360]/b" \
    --merge-output-format mp4 -o "media/bad_apple.%(ext)s" "$URL"
fi

if [ ! -f media/bad_apple.mp3 ]; then
  ffmpeg -loglevel error -y -i media/bad_apple.mp4 -vn -c:a libmp3lame -q:a 4 media/bad_apple.mp3
fi

echo "Ready: media/bad_apple.mp4 + media/bad_apple.mp3"
