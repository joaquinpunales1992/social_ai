import logging
import requests
from social.instagram.utils import publish_instagram_post, publish_instagram_reel
from social.facebook.utils import publish_facebook_post, publish_facebook_reel
import os

logger = logging.getLogger(__name__)


def post_on_instagram_tool():
    return publish_instagram_post()


def reel_on_instagram_tool():
    return publish_instagram_reel()


def post_on_facebook_tool():
    return publish_facebook_post()


def reel_on_facebook_tool():
    return publish_facebook_reel()


def search_image_tool(query: str, num_results: int = 5):
    import pdb

    pdb.set_trace()
    api_key = os.getenv("GOOGLE_API_KEY")
    cx = os.getenv("GOOGLE_CSE_ID")

    endpoint = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": query,
        "cx": cx,
        "key": api_key,
        "searchType": "image",
        "num": min(num_results, 10),
    }

    response = requests.get(endpoint, params=params)
    response.raise_for_status()
    data = response.json()

    return {"images": [item["link"] for item in data.get("items", [])]}


def available_properties_to_post():
    return [
        {"title": "Beatiful House in Tokyo", "price": 12000, "bedrooms": 3},
        {"title": "Beatiful House in Kyoto", "price": 24000, "bedrooms": 5},
        {"title": "Beatiful House in Osaka", "price": 19000, "bedrooms": 5},
    ]


tools = [
    # INSTAGRAM
    {
        "type": "function",
        "function": {
            "name": "post_on_instagram_tool",
            "strict": True,
            "description": "Posts an image carousel on Instagram. Use this when posting static images (e.g., of a property).",
            "parameters": {
                "type": "object",
                "properties": {
                    "property_id": {
                        "type": "string",
                        "description": "The ID of the property to be posted.",
                    },
                    "caption": {
                        "type": "string",
                        "description": "Caption for the Instagram post.",
                    },
                },
                "required": ["property_id", "caption"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "reel_on_instagram_tool",
            "strict": True,
            "description": "Posts a reel on Instagram. Use this when posting a video highlight of a property.",
            "parameters": {
                "type": "object",
                "properties": {
                    "property_id": {
                        "type": "string",
                        "description": "The ID of the property for which the reel will be created.",
                    },
                    "caption": {
                        "type": "string",
                        "description": "Caption for the Instagram reel.",
                    },
                },
                "required": ["property_id", "caption"],
            },
        },
    },
    # FACEBOOK
    {
        "type": "function",
        "function": {
            "name": "post_on_facebook_tool",
            "strict": True,
            "description": "Posts an image carousel on Facebook. Use this when posting static images (e.g., of a property).",
            "parameters": {
                "type": "object",
                "properties": {
                    "property_id": {
                        "type": "string",
                        "description": "The ID of the property to be posted.",
                    },
                    "caption": {
                        "type": "string",
                        "description": "Caption for the Facebook post.",
                    },
                },
                "required": ["property_id", "caption"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "reel_on_facebook_tool",
            "strict": True,
            "description": "Posts a reel on Facebook. Use this when posting a video highlight of a property.",
            "parameters": {
                "type": "object",
                "properties": {
                    "property_id": {
                        "type": "string",
                        "description": "The ID of the property for which the reel will be created.",
                    },
                    "caption": {
                        "type": "string",
                        "description": "Caption for the Facebook reel.",
                    },
                    "video_text_top": {
                        "type": "string",
                        "description": "Text that will be placed at the top of the video",
                    },
                },
                "required": ["property_id", "caption", "video_text_top"],
            },
        },
    },
    # INTERNET IMAGES
    {
        "type": "function",
        "function": {
            "name": "search_image_tool",
            "strict": True,
            "description": "Searches the internet for images related to a given topic or keyword using Google Custom Search.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The topic or keyword to search images for (e.g., 'traditional Japanese house').",
                    },
                    "num_results": {
                        "type": "integer",
                        "description": "The number of images to return (max 10).",
                        "default": 5,
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "available_properties_to_post",
            "strict": True,
            "description": "Obtain the available properties to post. Use this when you need to get which properties are available for posting",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]
