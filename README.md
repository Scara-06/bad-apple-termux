# Bad Apple!! in Termux

Plays the Bad Apple!! shadow-art video as live ASCII art in your terminal, with audio. Pure Python, no pip packages.

## Quick start

```bash
pkg install -y git
git clone https://github.com/<Scara-06>/bad-apple-termux
cd bad-apple-termux
./install.sh     # installs python, ffmpeg, mpv, yt-dlp
./run.sh         # downloads the video on first run, then plays
```

Zoom out your terminal first (pinch, or Volume Down + `-`) for a sharper picture.

## Options

```bash
./run.sh --fps 15        # lighter on slow phones
./run.sh --width 100     # force width in characters
./run.sh --invert        # light terminal themes
./run.sh --chars " .oO@" # custom character ramp (dark -> bright)
./run.sh --no-audio
```

Ctrl+C stops playback and restores your terminal.

## How it works

1. `ffmpeg` decodes the video into tiny grayscale frames sized to your terminal.
2. `badapple.py` maps each pixel to a character from a brightness ramp.
3. Frames are paced against a clock, and late frames are dropped so picture and audio stay in sync.
4. `mpv` plays the audio at the same moment (falls back to `termux-media-player` or `ffplay`).

## Notes

- The video is not included in this repo. `download.sh` fetches it with yt-dlp; pass your own URL as an argument, or drop your own file at `media/bad_apple.mp4`.
- No sound? Run `pkg install mpv`, and check your media volume.
- Choppy? Lower `--fps` or `--width`.

## Pushing your own copy to GitHub (from Termux)

```bash
pkg install -y git gh
gh auth login
git init && git add . && git commit -m "Bad Apple for Termux"
gh repo create bad-apple-termux --public --source=. --push
```
