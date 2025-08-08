# from social.models import SocialPost
from social.facebook.constants import FACEBOOK_PAGE_ID
import logging
import shutil
import os

# from django.conf import settings
import requests
import urllib.parse
from social.utils import (
    generate_caption,
    get_random_mp3_full_path,
    notify_social_token_expired,
    create_video,
)

from social.constants import *
from social.config.settings import settings


logger = logging.getLogger(__name__)


def prepare_image_url_for_facebook(image_url: str) -> str:
    image_url = image_url.lstrip("/")
    # Decode the URL twice
    decoded_once = urllib.parse.unquote(image_url)
    decoded_final = urllib.parse.unquote(decoded_once)

    # Ensure the URL starts with 'https://'
    if decoded_final.startswith("media/https:/"):
        image_url = decoded_final.replace("media/https:/", "https://", 1)
    elif decoded_final.startswith("https:/"):
        image_url = decoded_final.replace("https:/", "https://", 1)

    return image_url


def publish_facebook_post(
    content_data: dict,
    image_urls: list,
    hashtags: str,
    default_caption: str,
    last_caption_generated: str,
    facebook_page_id: str,
    meta_api_key: str,
    use_ai_caption: bool,
    internet_images: bool,
):
    """
    Generic function to post content to Facebook with multiple images.

    Args:
        content_data (dict): Contains information like location, url, price, etc.
        use_ai_caption (bool): Whether to generate an AI-based caption.
        get_caption_fn (function): Function to generate the caption text.
        get_fresh_token_fn (function): Function to retrieve a fresh Facebook token.
        get_image_urls_fn (function): Function to retrieve a list of image URLs.
        page_id (str): Facebook Page ID where the content should be posted.
    """
    # Step 1: Generate caption
    ai_caption, caption = generate_caption(
        content_data=content_data,
        default_caption=default_caption,
        last_caption_generated=last_caption_generated,
        hashtags=hashtags,
        use_ai_caption=use_ai_caption,
    )

    # Step 2: Upload images to Facebook
    media_fbids = []
    for raw_url in image_urls:
        try:
            if internet_images:
                image_url = raw_url
            else:
                image_url = (
                    f"http://127.0.0.1:8000/{prepare_image_url_for_facebook(raw_url)}"
                )

        except Exception as e:
            logger.error(f"Error preparing image URL: {e}")
            continue

        upload_url = f"https://graph.facebook.com/v19.0/{facebook_page_id}/photos"
        payload = {
            "url": image_url,
            "published": "false",
            "access_token": meta_api_key,
        }
        response = requests.post(upload_url, data=payload)

        result = response.json()

        if response.status_code == 200 and "id" in result:
            logger.info(f"Uploaded image: {image_url}")
            media_fbids.append(result["id"])
        else:
            logger.error(f"Failed to upload image: {result}")

    # Step 3: Post content with attached media
    if media_fbids:
        post_url = f"https://graph.facebook.com/v19.0/{facebook_page_id}/feed"
        payload = {
            "message": caption,
            "access_token": meta_api_key,
        }
        for i, media_id in enumerate(media_fbids):
            payload[f"attached_media[{i}]"] = f'{{"media_fbid":"{media_id}"}}'

        response = requests.post(post_url, data=payload)
        result = response.json()

        if response.status_code == 200:
            logger.info(f"Successfully posted to Facebook with multiple images.")
            # TODO: this needs to be more abstract
            # SocialPost.objects.create(
            #     caption=caption,
            #     post_identifier=content_data.get("receipe_pk"),
            #     social_media=FACEBOOK_SOCIAL_MEDIA,
            #     content_type=CONTENT_TYPE_POST,
            # )
        else:
            logger.error(f"Failed to create post: {result}")
    else:
        logger.error("No images were uploaded; skipping post.")


def publish_facebook_reel(
    content_data: dict,
    image_urls: list,
    hashtags: str,
    default_caption: str,
    last_caption_generated: str,
    facebook_page_id: str,
    meta_api_key: str,
    use_ai_caption: bool,
    last_reel_posted_sound_track: str,
    video_text: str = None,
    internet_images: bool = False,
):
    try:
        if not image_urls:
            logger.warning("No suitable property found to post on Facebook Reels.")
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

        media_dir = (
            "generated_videos"  # os.path.join(settings.MEDIA_ROOT, "generated_videos")
        )
        os.makedirs(media_dir, exist_ok=True)
        target_path = os.path.join(media_dir, "property_video.mp4")
        shutil.move("property_video.mp4", target_path)

        video_url = "https://social-ai-s1kk.onrender.com/media/generated_videos/property_video.mp4"

        ai_caption, caption = generate_caption(
            content_data=content_data,
            default_caption=default_caption,
            last_caption_generated=last_caption_generated,
            hashtags=hashtags,
            use_ai_caption=use_ai_caption,
        )

        # Step: Upload video to Facebook Page
        upload_url = f"https://graph.facebook.com/v19.0/{facebook_page_id}/videos"

        payload = {
            "file_url": video_url,
            "description": caption,
            "published": "true",
            "access_token": meta_api_key,
        }

        response = requests.post(upload_url, data=payload)
        logger.info("Facebook video upload response: " + response.text)

        if response.status_code == 200 and "id" in response.json():
            logger.info("Successfully posted to Facebook Reels!")
            import pdb

            pdb.set_trace()
        # Log the post
        # SocialPost.objects.create(
        #     ai_caption=ai_caption,
        #     caption=caption,
        #     post_identifier="",
        #     social_media=FACEBOOK_SOCIAL_MEDIA,
        #     content_type=CONTENT_TYPE_REEL,
        #     sound_track=audio_path,
        # )
        else:
            logger.error("Failed to post Facebook Reel: " + response.text)

    except Exception as e:
        logger.error(f"Error posting Facebook Reel: {e}")
        notify_social_token_expired(message=f"Error posting Facebook Reel: {e}")
