import os
import time
import requests
import shutil
import logging
from social.ai.cerebras import CerebrasAI
from social.utils import (
    get_fresh_token,
    generate_caption,
    notify_social_token_expired,
    get_random_mp3_full_path,
    create_video,
)
# from social.models import SocialComment, SocialPost
from social.config.settings import settings
from social.instagram.constants import (
    INSTAGRAM_USER_ID,
    DEFAULT_COMMENT,
    META_GRAPH_BASE_ENDPOINT,
    CREATED_VIDEO_PUBLIC_URL,
)
from social import utils as social_utils

logger = logging.getLogger(__name__)


def _reply_comment(comment_id: int, reply_message: str):
    url = f"{META_GRAPH_BASE_ENDPOINT}{comment_id}/replies"
    payload = {
        "message": reply_message,
        "access_token": get_fresh_token(),
    }
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        logger.info("Replied successfully!")
        return response.json()
    else:
        logger.error("Error replying:", response.text)
        return None


def _get_reels():
    url = f"{META_GRAPH_BASE_ENDPOINT}{INSTAGRAM_USER_ID}/media"
    params = {
        "fields": "id,caption,media_type",
        "access_token": get_fresh_token(),
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    media = response.json()["data"]
    # Filter Reels
    return [item for item in media if item["media_type"] == "VIDEO"]


def _get_comments_per_reel(media_id):
    url = f"{META_GRAPH_BASE_ENDPOINT}{media_id}/comments"
    params = {
        "access_token": get_fresh_token(),
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json().get("data", [])


def _reply_comments_instagram_post():
    pass


def _reply_comments_instagram_reels():
    reels = _get_reels()
    for reel in reels:
        comments = _get_comments_per_reel(reel["id"])
        reel_id = reel["id"]
        replied_social_comments_ids_per_reel = ""
        # replied_social_comments_ids_per_reel = SocialComment.objects.filter(
        #     Q(post=reel_id, replied=True) | Q(self_comment=True)
        # ).values_list("comment_id", flat=True)

        for comment in comments:
            comment_id = comment["id"]
            comment = comment["text"]

            if (
                int(comment_id) in replied_social_comments_ids_per_reel
                or comment == DEFAULT_COMMENT
            ):
                continue

            cerebras_ai_client = CerebrasAI()
            ai_comment = cerebras_ai_client.generate_text(
                prompt=(
                    f"Generate a friendly response for a social media comment. Encourage the person to check the link in our bio.\n\n"
                    "Output ONLY the caption. No bullet points, no quotes, no examples.\n\n"
                )
            )

            reply_message = _reply_comment(
                comment_id,
                ai_comment,
            )

            # SocialComment.objects.create(
            #     post=reel_id,
            #     comment_id=comment_id,
            #     comment=reply_message,
            #     replied=True if reply_message else False,
            #     self_comment=False,
            # )


def reply_comments_instagram():
    _reply_comments_instagram_reels()
    _reply_comments_instagram_post()


def publish_instagram_post(
    content_data: dict,
    image_urls: list,
    hashtags: str,
    default_caption: str,
    last_caption_generated: str,
    instagram_page_id: str,
    use_ai_caption: bool,
):
    """
    Generic function to post content to Instagram with multiple images.

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

    # Step 2: Upload images to Instagram
    media_fbids = []
    for image_url in image_urls:
        upload_url = f"{META_GRAPH_BASE_ENDPOINT}{INSTAGRAM_USER_ID}/media"
        payload = {
            "image_url": image_url,
            "is_carousel_item": True,
            "access_token": get_fresh_token(),
        }
        response = requests.post(upload_url, data=payload)
        result = response.json()

        if "id" in result:
            logger.info(f"Uploaded image for carousel: {image_url}")
            media_fbids.append(result["id"])
        else:
            logger.error(f"Failed to upload image: {result}")

    # Step 3: Post content with attached media
    if media_fbids:
        carousel_url = f"{META_GRAPH_BASE_ENDPOINT}{instagram_page_id}/media"
        payload = {
            "media_type": "CAROUSEL",
            "children": ",".join(media_fbids),
            "caption": caption,
            "access_token": get_fresh_token(),
        }

        carousel_response = requests.post(carousel_url, data=payload)
        result = carousel_response.json()

        if "id" in result:
            creation_id = result["id"]
            publish_url = f"{META_GRAPH_BASE_ENDPOINT}{instagram_page_id}/media_publish"
            publish_payload = {
                "creation_id": creation_id,
                "access_token": get_fresh_token(),
            }
            publish_response = requests.post(publish_url, data=publish_payload)
            if publish_response.status_code == 200:
                logger.info("Successfully posted carousel to Instagram.")
                # SocialPost.objects.create(
                #     caption=caption,
                #     property_url=property.url,
                #     social_media=INSTAGRAM_SOCIAL_MEDIA,
                # )
            else:
                logger.error(f"Failed to publish carousel: {publish_response.json()}")
        else:
            logger.error(f"Failed to create carousel container: {result}")
    else:
        logger.error("No media uploaded; skipping Instagram post.")


def publish_instagram_reel(
    content_data: dict,
    image_urls: list,
    hashtags: str,
    default_caption: str,
    last_caption_generated: str,
    instagram_page_id: str,
    use_ai_caption: bool,
    last_reel_posted_sound_track: str,
):
    try:
        if not image_urls:
            logger.warning("No suitable property found to post on Instagram Reels.")
            return

        audio_path = get_random_mp3_full_path(exclude=last_reel_posted_sound_track)
        create_video(
            images_urls=image_urls,
            output_path="property_video.mp4",
            audio_path=audio_path,
            duration_per_image=3,
        )

        media_dir = "generated_videos" # os.path.join(settings.MEDIA_ROOT, "generated_videos")
        os.makedirs(media_dir, exist_ok=True)
        target_path = os.path.join(media_dir, "property_video.mp4")
        shutil.move("property_video.mp4", target_path)

        ai_caption, caption = generate_caption(
            content_data=content_data,
            default_caption=default_caption,
            last_caption_generated=last_caption_generated,
            hashtags=hashtags,
            use_ai_caption=use_ai_caption,
        )

        # Step 1: Create media container
        media_url = f"{META_GRAPH_BASE_ENDPOINT}{instagram_page_id}/media"
        media_payload = {
            "media_type": "REELS",
            "video_url": CREATED_VIDEO_PUBLIC_URL,
            "caption": caption,
            "share_to_feed": False,
            "access_token": get_fresh_token(),
        }
        media_response = requests.post(media_url, data=media_payload)
        logger.info("Media upload response: " + media_response.text)

        time.sleep(180)
        if "id" in media_response.json():
            creation_id = media_response.json()["id"]

            # Step 2: Publish the video
            publish_url = f"{META_GRAPH_BASE_ENDPOINT}{instagram_page_id}/media_publish"
            publish_payload = {
                "creation_id": creation_id,
                "access_token": get_fresh_token(),
            }
            publish_response = requests.post(publish_url, data=publish_payload)
            logger.info("Publish response: " + publish_response.text)

            if publish_response.status_code == 200:
                media_id = publish_response.json().get("id")
                logger.info("✅ Successfully posted to Instagram Reels!")

                # Step 3: Add comment to the published Reel
                if media_id:
                    comment_payload = {
                        "message": DEFAULT_COMMENT,
                        "access_token": get_fresh_token(),
                    }
                    comment_url = f"{META_GRAPH_BASE_ENDPOINT}{media_id}/comments"
                    comment_response = requests.post(comment_url, data=comment_payload)
                    logger.info("Comment response: " + comment_response.text)

                    # SocialComment.objects.create(
                    #     post=creation_id,
                    #     comment_id=1,  # TODO: FIX
                    #     comment=comment_response,
                    #     replied=True if comment_response else False,
                    #     self_comment=True,
                    # )

                # Log the post
                # SocialPost.objects.create(
                #     ai_caption=ai_caption,
                #     caption=caption,
                #     property_url="",  # TODO
                #     social_media=social_utils.INSTAGRAM_SOCIAL_MEDIA,
                #     content_type=social_utils.CONTENT_TYPE_REEL,
                #     sound_track=audio_path,
                # )
            else:
                logger.error("Failed to publish Reel: " + publish_response.text)
        else:
            logger.error("Failed to create media container: " + media_response.text)
    except Exception as e:
        logger.error(f"Error posting Instagram Reel: {e}")
        notify_social_token_expired(message=f"Error posting Instagram Reel: {e}")
