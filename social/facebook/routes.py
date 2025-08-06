from fastapi import APIRouter
from social.facebook.models import FacebookPostRequest, FacebookReelRequest
from social.facebook.services import do_publish_facebook_post, do_publish_facebook_reel

router = APIRouter()


@router.post("/publish-facebook-post")
async def publish_facebook_post_url(data: FacebookPostRequest):
    return await do_publish_facebook_post(data)


@router.post("/publish-facebook-reel")
async def publish_facebook_reel_url(data: FacebookReelRequest):
    return await do_publish_facebook_reel(data)
