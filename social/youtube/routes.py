from fastapi import APIRouter
from social.youtube.models import YoutubeShortRequest
from social.youtube.services import do_publish_youtube_short

router = APIRouter()


@router.post("/publish-youtube-short")
async def publish_youtube_short_url(data: YoutubeShortRequest):
    return await do_publish_youtube_short(data)
