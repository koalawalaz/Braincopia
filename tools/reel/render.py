#!/usr/bin/env python3
"""Render tools/reel/reel.html frame by frame and encode it with ffmpeg.

    python3 tools/reel/render.py            # -> assets/video/braincopia-vol1.mp4
    python3 tools/reel/render.py --gif      # also writes a GIF beside it

The animation is deterministic: reel.html exposes setFrame(n), so every frame is
positioned by number rather than by wall clock. Re-running gives the same file.
Needs playwright with a Chromium build, and ffmpeg on PATH (or FFMPEG set).
"""
import argparse, os, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REEL = os.path.join(ROOT, "tools", "reel", "reel.html")
OUT = os.path.join(ROOT, "assets", "video", "braincopia-vol1.mp4")


def ffmpeg():
    exe = os.environ.get("FFMPEG") or shutil.which("ffmpeg")
    if exe:
        return exe
    try:                                    # pip install imageio-ffmpeg
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        sys.exit("ffmpeg not found. Install it, or set FFMPEG to its path.")


def render(frames_dir):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        launch = {"args": ["--no-sandbox", "--force-device-scale-factor=1"]}
        if os.environ.get("CHROMIUM"):
            launch["executable_path"] = os.environ["CHROMIUM"]
        b = p.chromium.launch(**launch)
        pg = b.new_page(viewport={"width": 1080, "height": 1350})
        pg.goto("file://" + REEL)
        pg.wait_for_timeout(1500)           # let the webfonts land
        total = pg.evaluate("window.TOTAL")
        stage = pg.query_selector("#stage")
        for n in range(total):
            pg.evaluate("window.setFrame(%d)" % n)
            stage.screenshot(path=os.path.join(frames_dir, "f%04d.png" % n))
        b.close()
    return total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gif", action="store_true", help="also write a GIF")
    args = ap.parse_args()

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with tempfile.TemporaryDirectory() as frames:
        total = render(frames)
        ff = ffmpeg()
        subprocess.run([ff, "-y", "-loglevel", "error", "-framerate", "25",
                        "-i", os.path.join(frames, "f%04d.png"),
                        "-c:v", "libx264", "-preset", "slow", "-crf", "18",
                        "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                        "-r", "25", OUT], check=True)
        if args.gif:
            subprocess.run([ff, "-y", "-loglevel", "error", "-i", OUT, "-vf",
                            "fps=12,scale=480:-1:flags=lanczos,split[a][b];"
                            "[a]palettegen=max_colors=128[p];"
                            "[b][p]paletteuse=dither=bayer:bayer_scale=3",
                            OUT.replace(".mp4", ".gif")], check=True)
    print("%d frames -> %s" % (total, OUT))


if __name__ == "__main__":
    main()
