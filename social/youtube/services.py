from social.youtube.models import YoutubeShortRequest
from social.youtube.utils import publish_youtube_short, run_publish_youtube_short
from social.config.settings import settings


async def do_publish_youtube_short(data: YoutubeShortRequest):
    print("Posting to Youtube short:", data)

    data_dict = data.model_dump()

    response = publish_youtube_short(
        data_dict.get("content_data"),
        data_dict.get("image_urls"),
        data_dict.get("hashtags"),
        data_dict.get("default_caption"),
        data_dict.get("last_caption_generated"),
        data_dict.get("client_secret"),
        data_dict.get("use_ai_caption"),
        data_dict.get("last_reel_posted_sound_track"),
        data_dict.get("video_text"),
        data_dict.get("internet_images"),
    )
    return {"status": response, "data": data.model_dump()}