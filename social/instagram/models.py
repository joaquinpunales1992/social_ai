from pydantic import BaseModel
from typing import List, Optional


class InstagramPostRequest(BaseModel):
    content_data: str
    image_urls: List[str]
    hashtags: List[str]
    default_caption: Optional[str] = None
    last_caption_generated: Optional[str] = None
    instagram_page_id: str
    meta_api_key: str
    use_ai_caption: bool = True


class InstagramReelRequest(BaseModel):
    content_data: str
    image_urls: List[str]
    hashtags: List[str]
    default_caption: Optional[str] = None
    last_caption_generated: str
    instagram_page_id: str
    meta_api_key: str
    use_ai_caption: bool = True
    last_reel_posted_sound_track: str
    video_text: str
