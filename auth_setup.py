"""
Run this ONCE to get your YouTube refresh token.
It will open a browser window for you to authorize the app.
Save the refresh token in your .env file.
"""

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def main():
    print("=== YouTube OAuth Setup ===")
    print()
    print("Before running this, you need to:")
    print("1. Go to https://console.cloud.google.com/")
    print("2. Create a project (or use existing)")
    print("3. Enable 'YouTube Data API v3'")
    print("4. Go to Credentials > Create Credentials > OAuth Client ID")
    print("5. Choose 'Desktop app' as the application type")
    print("6. Download the client_secret JSON file")
    print("7. Save it as 'client_secret.json' in this folder")
    print()

    flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
    credentials = flow.run_local_server(port=8080)

    print()
    print("=== SUCCESS ===")
    print(f"Refresh Token: {credentials.refresh_token}")
    print()
    print("Add this to your .env file as YOUTUBE_REFRESH_TOKEN")


if __name__ == "__main__":
    main()
