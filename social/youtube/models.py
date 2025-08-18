from pydantic import BaseModel
from typing import List, Optional


class YoutubeShortRequest(BaseModel):
    content_data: str
    image_urls: List[str]
    hashtags: List[str]
    default_caption: Optional[str] = None
    last_caption_generated: Optional[str] = None
    facebook_page_id: str
    meta_api_key: str
    use_ai_caption: bool = True
    internet_images: bool = False
