from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from config import YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def get_youtube_service():
    credentials = Credentials(
        token=None,
        refresh_token=YOUTUBE_REFRESH_TOKEN,
        client_id=YOUTUBE_CLIENT_ID,
        client_secret=YOUTUBE_CLIENT_SECRET,
        token_uri="https://oauth2.googleapis.com/token",
    )
    return build("youtube", "v3", credentials=credentials)


def upload_short(video_path, title, description):
    youtube = get_youtube_service()

    body = {
        "snippet": {
            "title": f"{title} | Classic Cartoon #Shorts",
            "description": (
                f"{description}\n\n"
                "Who remembers watching this as a kid?\n\n"
                "#shorts #cartoon #classicCartoon #superman #popeye "
                "#bettyboop #vintage #animation #retro #nostalgia "
                "#oldcartoons #childhoodmemories #throwback #cartoons "
                "#classicanimation #vintagecartoon #kidscartoon"
            ),
            "tags": [
                "shorts", "cartoon", "classic cartoon", "superman cartoon",
                "popeye", "betty boop", "vintage cartoon", "animation",
                "retro cartoon", "nostalgia", "old cartoons", "classic animation",
                "childhood memories", "throwback", "kids cartoon",
                "cartoon nostalgia", "old school cartoon", "vintage animation",
            ],
            "categoryId": "24",
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload(str(video_path), mimetype="video/mp4", resumable=True)

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media,
    )

    response = None
    while response is None:
        _, response = request.next_chunk()

    video_id = response["id"]
    print(f"YouTube upload complete: https://youtube.com/shorts/{video_id}")
    return video_id
