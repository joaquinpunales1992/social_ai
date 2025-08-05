from fastapi import APIRouter
from social.instagram.models import InstagramPostRequest, InstagramReelRequest
from social.instagram.services import do_publish_instagram_post, do_publish_instagram_reel
router = APIRouter()

@router.post("/publish-instagram-post")
async def publish_facebook_post_url(data: InstagramPostRequest):
    return await do_publish_instagram_post(data)

@router.post("/publish-instagram-reel")
async def publish_facebook_reel_url(data: InstagramReelRequest):
    return await do_publish_instagram_reel(data)

@router.post("/reply-instagram-reel-comments")
async def publish_facebook_reel_url(data: InstagramReelRequest):
    return await do_publish_instagram_reel(data)
