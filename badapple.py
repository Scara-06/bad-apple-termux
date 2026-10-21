#!/usr/bin/env python3
"""Play Bad Apple!! as ASCII art in the terminal (built for Termux).

Pure Python, no pip packages. ffmpeg decodes the video into tiny grayscale
frames, Python maps each pixel to a character, and audio is played by mpv
(or termux-media-player / ffplay if mpv is missing).
"""
import argparse
import os
import shutil
import signal
import subprocess
import sys
import time

RAMP = " .:-=+*#%@"  # dark -> bright


def probe_size(path):
    """Return (width, height) of the video, falling back to 480x360."""
    try:
        out = subprocess.check_output(
            ["ffprobe", "-v", "error", "-select_streams", "v:0",
             "-show_entries", "stream=width,height", "-of", "csv=p=0", path],
            stderr=subprocess.DEVNULL, text=True,
        ).strip()
        w, h = out.split(",")[:2]
        return int(w), int(h)
    except Exception:
        return 480, 360


def make_table(ramp, invert):
    if invert:
        ramp = ramp[::-1]
    n = len(ramp)
    return bytes(ord(ramp[min(g * n // 256, n - 1)]) for g in range(256))


def start_audio(path):
    """Start audio playback; return a function that stops it."""
    if not path or not os.path.exists(path):
        return lambda: None
    if shutil.which("mpv"):
        p = subprocess.Popen(
            ["mpv", "--no-video", "--really-quiet", "--no-terminal", path],
            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return lambda: (p.terminate(), p.wait())
    if shutil.which("termux-media-player"):
        subprocess.run(["termux-media-player", "play", path],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return lambda: subprocess.run(["termux-media-player", "stop"],
                                      stdout=subprocess.DEVNULL,
                                      stderr=subprocess.DEVNULL)
    if shutil.which("ffplay"):
        p = subprocess.Popen(
            ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", path],
            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return lambda: (p.terminate(), p.wait())
    print("No audio player found (install mpv). Playing silent.", file=sys.stderr)
    time.sleep(1.5)
    return lambda: None


def main():
    ap = argparse.ArgumentParser(description="Bad Apple!! in your terminal")
    ap.add_argument("--video", default="media/bad_apple.mp4")
    ap.add_argument("--audio", default="media/bad_apple.mp3")
    ap.add_argument("--fps", type=int, default=30,
                    help="playback fps (lower it if your phone lags)")
    ap.add_argument("--width", type=int, default=0,
                    help="force width in characters (default: fit screen)")
    ap.add_argument("--invert", action="store_true",
                    help="swap light/dark (use on light terminals)")
    ap.add_argument("--chars", default=RAMP,
                    help="character ramp, dark to bright")
    ap.add_argument("--no-audio", action="store_true")
    args = ap.parse_args()

    if not os.path.exists(args.video):
        sys.exit(f"Video not found: {args.video}\nRun ./download.sh first.")
    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg missing. Run ./install.sh first.")

    cols, rows = shutil.get_terminal_size((80, 24))
    rows -= 1  # keep the last line free so the screen never scrolls
    vw, vh = probe_size(args.video)
    # Terminal cells are ~2x taller than wide.
    cell_ratio = 0.5
    max_w = args.width or cols
    w = max(8, min(max_w, int(rows / (vh / vw * cell_ratio))))
    h = max(4, int(w * vh / vw * cell_ratio))
    pad = b" " * max(0, (cols - w) // 2)

    table = make_table(args.chars, args.invert)
    frame_size = w * h

    ffmpeg = subprocess.Popen(
        ["ffmpeg", "-loglevel", "error", "-i", args.video,
         "-vf", f"fps={args.fps},scale={w}:{h}:flags=area",
         "-pix_fmt", "gray", "-f", "rawvideo", "-"],
        stdout=subprocess.PIPE, stdin=subprocess.DEVNULL,
        bufsize=frame_size * 8,
    )

    out = sys.stdout.buffer
    stop_audio = lambda: None

    def cleanup(*_):
        try:
            stop_audio()
        except Exception:
            pass
        if ffmpeg.poll() is None:
            ffmpeg.kill()
        out.write(b"\x1b[0m\x1b[?25h\x1b[?1049l")  # show cursor, leave alt screen
        out.flush()

    signal.signal(signal.SIGTERM, lambda *a: (cleanup(), sys.exit(0)))

    out.write(b"\x1b[?1049h\x1b[?25l\x1b[2J")  # alt screen, hide cursor, clear
    out.flush()
    try:
        if not args.no_audio:
            stop_audio = start_audio(args.audio)
        start = time.perf_counter()
        n = 0
        frame_time = 1.0 / args.fps
        while True:
            data = ffmpeg.stdout.read(frame_size)
            if len(data) < frame_size:
                break
            target = start + n * frame_time
            now = time.perf_counter()
            n += 1
            if now - target > frame_time:
                continue  # running late: drop this frame to stay in sync
            if target > now:
                time.sleep(target - now)
            lines = [pad + data[i * w:(i + 1) * w].translate(table)
                     for i in range(h)]
            out.write(b"\x1b[H" + b"\n".join(lines))
            out.flush()
    except KeyboardInterrupt:
        pass
    finally:
        cleanup()


if __name__ == "__main__":
    main()
