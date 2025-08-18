# from social.models import SocialPost
from social.facebook.constants import FACEBOOK_PAGE_ID
import logging
import json
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from social.utils import (
    generate_caption,
    get_random_mp3_full_path,
    notify_social_token_expired,
    create_video,
)

import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


from social.constants import *
from social.config.settings import settings


logger = logging.getLogger(__name__)


# YouTube Data API scope
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def get_youtube_credentials(client_secret: json):
    creds = None
    # Token will be saved in token.pickle after first login
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    # If no valid creds, start login flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_config(client_secret, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save for next runs
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    return creds


def publish_youtube_short(
    content_data: dict,
    image_urls: list,
    hashtags: str,
    default_caption: str,
    last_caption_generated: str,
    client_secret: json,
    use_ai_caption: bool,
    last_reel_posted_sound_track: str,
    video_text: str = None,
    internet_images: bool = False,
):
    try:
        youtube_credentials = get_youtube_credentials(client_secret=client_secret)
        if not image_urls:
            logger.warning("No suitable property found to post on YouTube Shorts.")
            return

        # Create video
        audio_path = get_random_mp3_full_path(exclude=last_reel_posted_sound_track)
        create_video(
            images_urls=image_urls,
            output_path="property_video.mp4",
            audio_path=audio_path,
            video_text=video_text,
            duration_per_image=3,
            internet_images=internet_images,
        )

        ai_caption, caption = generate_caption(
            content_data=content_data,
            default_caption=default_caption,
            last_caption_generated=last_caption_generated,
            hashtags=hashtags,
            use_ai_caption=use_ai_caption,
        )

        # Build YouTube service
        youtube = build("youtube", "v3", credentials=youtube_credentials)

        # Upload video (must be vertical + <60s for Shorts)
        media = MediaFileUpload("property_video.mp4", chunksize=-1, resumable=True)

        request = youtube.videos().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": caption[:95], 
                    "description": caption,
                    "tags": hashtags.split(),  
                    "categoryId": "22",
                },
                "status": {
                    "privacyStatus": "public"
                }
            },
            media_body=media
        )

        response = request.execute()
        logger.info("YouTube upload response: " + str(response))

        if "id" in response:
            video_id = response["id"]
            logger.info(f"Successfully posted YouTube Short! Video ID: {video_id}")
        else:
            logger.error("Failed to upload YouTube Short: " + str(response))

    except Exception as e:
        logger.error(f"Error posting YouTube Short: {e}")
        notify_social_token_expired(message=f"Error posting YouTube Short: {e}")




# def run_publish_youtube_short():
    
    # publish_youtube_short(
    #     content_data= "A cool House in Japan, can you belive it?",
    #     image_urls= ["https://jlifeinternational.com/cdn/shop/articles/pexels-pixabay-161247.jpg?v=1623096114&width=1500", "https://jlifeinternational.com/cdn/shop/articles/pexels-pixabay-161247.jpg?v=1623096114&width=1500"],
    #     hashtags= "#japan",
    #     default_caption= "Look at this House!",
    #     last_caption_generated= "",
    #     client_secret=
    #     last_reel_posted_sound_track= "",
    #     video_text= "Buy now!",
    #     internet_images= True,
    # )
