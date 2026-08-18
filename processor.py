import subprocess
from pathlib import Path
from config import PROCESSED_DIR


def create_short(video_path, cartoon_info):
    start = cartoon_info["start"]
    duration = cartoon_info["duration"]
    part = cartoon_info["part"]

    output_name = f"{video_path.stem}_part{part}_short.mp4"
    short_path = PROCESSED_DIR / output_name
    reel_path = PROCESSED_DIR / f"{video_path.stem}_part{part}_reel.mp4"

    _render_clip(video_path, short_path, start, duration)
    _render_clip(video_path, reel_path, start, duration)

    return short_path, reel_path


def _render_clip(input_path, output_path, start, duration):
    if output_path.exists():
        output_path.unlink()

    subprocess.run(
        [
            "ffmpeg", "-y",
            "-ss", str(start),
            "-i", str(input_path),
            "-t", str(duration),
            "-vf", (
                "scale=1080:1920:force_original_aspect_ratio=decrease,"
                "pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black"
            ),
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "23",
            "-c:a", "aac",
            "-b:a", "128k",
            "-movflags", "+faststart",
            str(output_path),
        ],
        capture_output=True, text=True, check=True,
    )

    return output_path
