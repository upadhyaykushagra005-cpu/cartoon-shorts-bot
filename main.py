import sys
import traceback
from source import find_cartoon, download_cartoon
from processor import create_short
from history import mark_posted
from config import PROCESSED_DIR, VIDEO_HOST_BASE_URL, YOUTUBE_REFRESH_TOKEN, INSTAGRAM_ACCESS_TOKEN


def run():
    print("=" * 50)
    print("CARTOON SHORTS BOT - Starting run")
    print("=" * 50)

    print("\nFinding a cartoon clip...")
    cartoon = find_cartoon()
    if not cartoon:
        print("No new clips found. All parts have been posted or no cartoons available.")
        sys.exit(0)

    print(f"\nSelected: {cartoon['title']}")
    print(f"  Start: {cartoon['start']:.0f}s | Duration: {cartoon['duration']:.0f}s")

    video_path = download_cartoon(cartoon)

    print("\nProcessing into short/reel format...")
    try:
        short_path, reel_path = create_short(video_path, cartoon)
        print(f"  Created: {short_path.name}")
    except Exception as e:
        print(f"Processing failed: {e}")
        traceback.print_exc()
        sys.exit(1)

    title = cartoon["title"]
    description = cartoon["description"]
    caption = (
        f"\U0001f3ac {title}\n\n"
        "Who remembers this? Drop a comment!\n\n"
        "#cartoon #classic #vintage #animation #retro #nostalgia #shorts "
        "#oldcartoons #childhoodmemories"
    )

    if YOUTUBE_REFRESH_TOKEN:
        print("\nUploading to YouTube...")
        try:
            from youtube_upload import upload_short
            upload_short(short_path, title, description)
        except Exception as e:
            print(f"YouTube upload failed: {e}")
            traceback.print_exc()
    else:
        print("\nSkipping YouTube: no credentials configured.")

    if INSTAGRAM_ACCESS_TOKEN:
        print("\nUploading to Instagram...")
        try:
            if VIDEO_HOST_BASE_URL:
                from instagram_upload import upload_reel
                video_url = f"{VIDEO_HOST_BASE_URL}/{reel_path.name}"
                upload_reel(video_url, caption)
            else:
                print("Skipping Instagram: VIDEO_HOST_BASE_URL not set.")
        except Exception as e:
            print(f"Instagram upload failed: {e}")
            traceback.print_exc()
    else:
        print("\nSkipping Instagram: no credentials configured.")

    mark_posted(cartoon["identifier"])

    print("\nCleaning up processed files...")
    for f in PROCESSED_DIR.iterdir():
        f.unlink()

    # Auto-delete source video if all its parts have been posted
    video_path = cartoon["video_path"]
    video_stem = video_path.stem
    from source import _get_duration, CLIP_DURATION
    try:
        duration = _get_duration(video_path)
        total_parts = 0
        start = 0
        while start + 10 < duration:
            clip_len = min(CLIP_DURATION, duration - start)
            if clip_len < 10:
                break
            total_parts += 1
            start += CLIP_DURATION

        from history import all_parts_posted
        if all_parts_posted(video_stem, total_parts):
            video_path.unlink()
            print(f"\nAll {total_parts} parts posted — deleted {video_path.name} to free space.")
    except Exception:
        pass

    print(f"\nDone! Posted: {title}")
    print("=" * 50)


if __name__ == "__main__":
    run()
