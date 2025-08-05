from pydantic import BaseModel
from typing import List, Optional


class InstagramPostRequest(BaseModel):
    content_data: str
    image_urls: List[str]
    hashtags: List[str]
    default_caption: Optional[str] = None
    last_caption_generated: Optional[str] = None
    page_id: str
    use_ai_caption: bool = True
    internet_images: bool = False

class InstagramReelRequest(BaseModel):
    content_data: str
    image_urls: List[str]
    hashtags: List[str]
    default_caption: Optional[str] = None
    facebook_page_id: str
    use_ai_caption: bool = True
    last_reel_posted_sound_track: str
    last_caption_generated: str
    video_text: str