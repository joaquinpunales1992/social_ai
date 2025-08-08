from social.instagram.models import InstagramPostRequest, InstagramReelRequest
from social.instagram.utils import (
    publish_instagram_post,
    publish_instagram_reel,
    reply_comments_instagram,
)
from social.config.settings import settings


async def do_publish_instagram_post(data: InstagramPostRequest):
    print("Posting to Instagram page")

    data_dict = data.model_dump()

    response = publish_instagram_post(
        data_dict.get("content_data"),
        data_dict.get("image_urls"),
        data_dict.get("hashtags"),
        data_dict.get("default_caption"),
        data_dict.get("last_caption_generated"),
        data_dict.get("instagram_page_id"),
        data_dict.get("meta_api_key"),
        data_dict.get("use_ai_caption"),
        data_dict.get("internet_images"),
    )
    return {"status": response, "data": data.model_dump()}


async def do_publish_instagram_reel(data: InstagramReelRequest):
    print("Posting to Instagram page")

    data_dict = data.model_dump()

    response = publish_instagram_reel(
        data_dict.get("content_data"),
        data_dict.get("image_urls"),
        data_dict.get("hashtags"),
        data_dict.get("default_caption"),
        data_dict.get("last_caption_generated"),
        data_dict.get("instagram_page_id"),
        data_dict.get("meta_api_key"),
        data_dict.get("use_ai_caption"),
        data_dict.get("last_reel_posted_sound_track"),
        data_dict.get("video_text"),

    )
    return {"status": response, "data": data.model_dump()}


# async def do_reply_instagram_comments()
