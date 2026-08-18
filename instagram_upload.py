import time
import requests
from config import INSTAGRAM_ACCESS_TOKEN, INSTAGRAM_BUSINESS_ACCOUNT_ID

GRAPH_API_BASE = "https://graph.facebook.com/v21.0"


def upload_reel(video_url, caption):
    container_id = _create_container(video_url, caption)
    _wait_for_processing(container_id)
    media_id = _publish(container_id)
    print(f"Instagram Reel published: {media_id}")
    return media_id


def _create_container(video_url, caption):
    url = f"{GRAPH_API_BASE}/{INSTAGRAM_BUSINESS_ACCOUNT_ID}/media"
    resp = requests.post(url, data={
        "media_type": "REELS",
        "video_url": video_url,
        "caption": caption,
        "access_token": INSTAGRAM_ACCESS_TOKEN,
    })
    resp.raise_for_status()
    return resp.json()["id"]


def _wait_for_processing(container_id, timeout=300):
    url = f"{GRAPH_API_BASE}/{container_id}"
    start = time.time()

    while time.time() - start < timeout:
        resp = requests.get(url, params={
            "fields": "status_code",
            "access_token": INSTAGRAM_ACCESS_TOKEN,
        })
        resp.raise_for_status()
        status = resp.json().get("status_code")

        if status == "FINISHED":
            return
        if status == "ERROR":
            raise RuntimeError(f"Instagram container {container_id} failed processing")

        time.sleep(10)

    raise TimeoutError(f"Instagram processing timed out after {timeout}s")


def _publish(container_id):
    url = f"{GRAPH_API_BASE}/{INSTAGRAM_BUSINESS_ACCOUNT_ID}/media_publish"
    resp = requests.post(url, data={
        "creation_id": container_id,
        "access_token": INSTAGRAM_ACCESS_TOKEN,
    })
    resp.raise_for_status()
    return resp.json()["id"]
