import json
import random
import subprocess
import internetarchive
from pathlib import Path
from config import DOWNLOADS_DIR
from history import is_posted

CLIP_DURATION = 59

COLLECTIONS = [
    "collection:classic_cartoons AND mediatype:movies",
    "collection:moviesandfilms AND subject:cartoon AND mediatype:movies",
    "collection:prelinger AND subject:animation AND mediatype:movies",
]

KNOWN_ITEMS = [
    # Superman (Fleischer) - all 17 confirmed public domain
    "superman_mechanical_monsters",
    "Superman-BillionDollarLimited",
    "superman_arcticgiant",
    "superman_bulleteers",
    "superman_magnetictelescope",
    "superman_electricearthquake",
    "superman_volcano",
    "superman_terroronthemidway",
    "superman_destroyinc",
    "superman_theundergroundworld",
    # Betty Boop
    "BettyBoop-IHeared1932",
    "Betty_Boops_Crazy_Inventions_1933",
    "Betty_Boop_Snow_White_1933",
    "betty_boop_minnie_the_moocher_1932",
    "bb_rhythmontheReservation",
    "bb_dizzyDishes",
    "The_Candid_Candidate",
    # Popeye
    "Popeye_Meets_Sindbad_the_Sailor",
    "popeye_floorFlusher",
    "popeye_me_musical_nephews",
    "PopeyeMeetsAliBaba",
    # Casper / Woody / Others
    "CasperTheFriendlyGhost1945",
    "WoodyWoodpeckerPantryPanic",
    "Steamboat_Willie",
    "FLIP_FROG-FIDDLESTICKS",
    "PortkyInWackyland",
    "AllThisAndRabbitStew1941",
    "MightyMouse_WolfWolf1944",
    # More classics
    "TheMadScientist",
    "GulliverSTravels",
    "felix_the_cat_feline_follies_1919",
    "little_lulu_eggs_dont_bounce",
    "heckle_jeckle_talkingmagpies",
]


def _get_duration(video_path):
    result = subprocess.run(
        [
            "ffprobe", "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            str(video_path),
        ],
        capture_output=True, text=True,
    )
    info = json.loads(result.stdout)
    return float(info["format"]["duration"])


def _find_video_file(item):
    preferred_formats = [".mp4", ".ogv", ".avi", ".mov", ".mkv", ".mpeg", ".mpg"]
    files = list(item.get_files())

    for fmt in preferred_formats:
        for f in files:
            name = f.name.lower()
            if name.endswith(fmt) and "thumb" not in name:
                return f
    return None


def _get_candidates():
    candidates = []

    for identifier in KNOWN_ITEMS:
        candidates.append(identifier)

    for query in COLLECTIONS:
        try:
            results = list(internetarchive.search_items(query, params={"rows": 30}))
            for r in results:
                if r["identifier"] not in candidates:
                    candidates.append(r["identifier"])
        except Exception:
            continue

    random.shuffle(candidates)
    return candidates


def _check_local_downloads():
    """Check already-downloaded files first before hitting the network."""
    video_exts = {".mp4", ".ogv", ".avi", ".mov", ".mkv", ".mpeg", ".mpg"}
    files = [f for f in DOWNLOADS_DIR.iterdir() if f.suffix.lower() in video_exts and f.stat().st_size > 500_000]
    random.shuffle(files)

    for video_path in files:
        try:
            duration = _get_duration(video_path)
            identifier = video_path.stem
            title = identifier.replace("_", " ").replace("-", " ").strip()
            # Clean up ugly names
            for remove in ["512kb", "256k", ".ia", "  "]:
                title = title.replace(remove, "")
            title = title.strip().title()

            part_num = 1
            start = 0
            while start + 10 < duration:
                clip_len = min(CLIP_DURATION, duration - start)
                if clip_len < 10:
                    break
                clip_id = f"{identifier}_part{part_num}"
                if not is_posted(clip_id):
                    return {
                        "identifier": clip_id,
                        "title": f"{title} - Part {part_num}",
                        "description": f"Classic cartoon - {title} Part {part_num}",
                        "video_path": video_path,
                        "start": start,
                        "duration": clip_len,
                        "part": part_num,
                    }
                start += CLIP_DURATION
                part_num += 1
        except Exception:
            continue
    return None


def find_cartoon():
    # First check already downloaded files
    local = _check_local_downloads()
    if local:
        return local

    # Then try downloading new ones
    candidates = _get_candidates()

    for identifier in candidates:
        try:
            item = internetarchive.get_item(identifier)
            title = item.metadata.get("title", identifier)
            title = title.replace("_", " ").strip()

            video_file = _find_video_file(item)
            if not video_file:
                continue

            safe_name = video_file.name.replace(" ", "_")
            dest = DOWNLOADS_DIR / safe_name
            if not dest.exists():
                print(f"Downloading: {title} ({video_file.name})")
                try:
                    import requests as req
                    download_url = f"https://archive.org/download/{identifier}/{video_file.name}"
                    resp = req.get(download_url, stream=True, timeout=120)
                    resp.raise_for_status()
                    with open(str(dest), "wb") as f:
                        for chunk in resp.iter_content(chunk_size=8192):
                            f.write(chunk)
                except Exception as dl_err:
                    print(f"Download failed for {identifier}: {dl_err}")
                    if dest.exists():
                        dest.unlink()
                    continue

            if not dest.exists():
                continue

            duration = _get_duration(dest)
            part_num = 1
            start = 0

            while start + 10 < duration:
                clip_len = min(CLIP_DURATION, duration - start)
                if clip_len < 10:
                    break

                clip_id = f"{identifier}_part{part_num}"
                if not is_posted(clip_id):
                    return {
                        "identifier": clip_id,
                        "title": f"{title} - Part {part_num}",
                        "description": f"Classic cartoon - {title} Part {part_num}",
                        "video_path": dest,
                        "start": start,
                        "duration": clip_len,
                        "part": part_num,
                    }

                start += CLIP_DURATION
                part_num += 1

        except Exception as e:
            print(f"Skipping {identifier}: {e}")
            continue

    return None


def download_cartoon(cartoon_info):
    return cartoon_info["video_path"]
