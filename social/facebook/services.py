from social.facebook.models import FacebookPostRequest, FacebookReelRequest
from social.facebook.utils import publish_facebook_post, publish_facebook_reel
from social.config.settings import settings


async def do_publish_facebook_post(data: FacebookPostRequest):
    print("Posting to Facebook page:", data)

    data_dict = data.model_dump()

    response = publish_facebook_post(
        data_dict.get("content_data"),
        data_dict.get("image_urls"),
        data_dict.get("hashtags"),
        data_dict.get("default_caption"),
        data_dict.get("last_caption_generated"),
        data_dict.get("facebook_page_id"),
        data_dict.get("meta_api_key"),
        data_dict.get("use_ai_caption"),
        data_dict.get("internet_images"),
    )
    return {"status": response, "data": data.model_dump()}


async def do_publish_facebook_reel(data: FacebookReelRequest):
    print("Posting to Facebook page:")

    data_dict = data.model_dump()

    response = publish_facebook_reel(
        data_dict.get("content_data"),
        data_dict.get("image_urls"),
        data_dict.get("hashtags"),
        data_dict.get("default_caption"),
        data_dict.get("last_caption_generated"),
        data_dict.get("facebook_page_id"),
        data_dict.get("meta_api_key"),
        data_dict.get("use_ai_caption"),
        data_dict.get("last_reel_posted_sound_track"),
        data_dict.get("video_text"),
        data_dict.get("internet_images"),
    )
    return {"status": response, "data": data.model_dump()}
