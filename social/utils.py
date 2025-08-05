from social.ai.cerebras import CerebrasAI
from fastapi_mail import ConnectionConfig
from fastapi_mail import FastMail, MessageSchema
from social import constants as social_constants
from moviepy.video.VideoClip import ImageClip
from moviepy import (
    ImageClip,
    concatenate_videoclips,
    TextClip,
    CompositeVideoClip,
    VideoFileClip,
)
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
import logging
import tempfile
import re
import urllib
import json
import random
import requests
import os


logger = logging.getLogger(__name__)


def get_fresh_token():
    try:
        with open("social_access_token.json", "r") as f:
            return json.load(f)["access_token"]
    except (FileNotFoundError, KeyError):
        return None


def _sanity_check_ai_caption(ai_caption: str) -> str:
    ai_caption = ai_caption.replace('"', "")

    reversed_text = ai_caption[::-1]
    match = re.search(r"[.!?]", reversed_text)
    if match:
        cut_index = len(ai_caption) - match.start()
        return ai_caption[:cut_index]
    return ai_caption.strip()


def generate_caption(
    content_data: dict,
    default_caption: str,
    hashtags: str,
    last_caption_generated: str,
    use_ai_caption: bool,
) -> str:
    ai_caption = ""
    if use_ai_caption:
        try:
            prompt = (
                f"Create a caption for a Facebook post with the following content:\n"
                f"{content_data}"
            )
            cerebras_ai_client = CerebrasAI()
            ai_caption = cerebras_ai_client.generate_text(
                prompt=(
                    f"{prompt}\n\n"
                    f"NOTE that the last caption created was {last_caption_generated} so try to avoid the same texting.\n\n"
                    "Output ONLY the caption. No bullet points, no quotes, no examples."
                )
            )

            ai_caption = _sanity_check_ai_caption(ai_caption)

            caption = ai_caption + f"\n\n{default_caption}\n\n{hashtags}"
            logger.info(f"Caption generated via AI: {caption}")
        except Exception as e:
            caption = f"{default_caption}\n\n{hashtags}"
            logger.error(f"AI caption generation failed: {e}")
        return ai_caption, caption
    else:
        logger.info("AI caption generation is disabled, using default caption format.")
        return (ai_caption, f"{default_caption}\n\n{hashtags}")


def prepare_image_url_for_facebook(image_url: str) -> str:
    image_url = image_url.lstrip("/")
    # Decode the URL twice
    decoded_once = urllib.parse.unquote(image_url)
    decoded_final = urllib.parse.unquote(decoded_once)

    # Ensure the URL starts with 'https://'
    if decoded_final.startswith("media/https:/"):
        image_url = decoded_final.replace("media/https:/", "https://", 1)
    elif decoded_final.startswith("https:/"):
        image_url = decoded_final.replace("https:/", "https://", 1)

    return image_url


def create_video(
    images_urls: list,
    output_path: str,
    audio_path: str,
    video_text: str = None,
    duration_per_image: int = 3,
):
    clips = []

    for image_url in images_urls:
        img_url = prepare_image_url_for_facebook(image_url)
        logger.info(f"Preparing image URL: {img_url}")
        try:
            local_path = download_image_to_tempfile(img_url)
            clip = ImageClip(local_path, duration=duration_per_image)

            if clip.w % 2 != 0 or clip.h % 2 != 0:
                clip = clip.resized((clip.w + (clip.w % 2), clip.h + (clip.h % 2)))

            clips.append(clip)
        except Exception as e:
            logger.warning(f" Skipping image {img_url}: {e}")

    if not clips:
        logger.error("No valid images to create video.")
        return

    final_video = concatenate_videoclips(clips, method="compose")

    # Write final video
    final_video.write_videofile(
        "property_video_without_label.mp4",
        fps=30,
        codec="libx264",
        audio=audio_path,
        bitrate="3500k",
        preset="medium",
        ffmpeg_params=[
            "-profile:v",
            "high",
            "-level",
            "4.1",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            "-g",
            "60",
            "-sc_threshold",
            "0",
        ],
    )

    clip_duration = len(images_urls)
    clip = VideoFileClip("property_video_without_label.mp4").subclipped(
        0, clip_duration
    )

    text_clip = (
        TextClip(
            font="social/assets/fonts/Montserrat-Bold.ttf",
            text=video_text,
            font_size=30,
            color="white",
        )
        .with_duration(clip_duration)
        .with_position((0.1, 0.7), relative=True)
    )

    text_clip_top = (
        TextClip(
            font="social/assets/fonts/Montserrat-Light.ttf",
            text="Link in Bio \n ",
            font_size=30,
            color="white",
        )
        .with_duration(clip_duration)
        .with_position(("center", 0.03), relative=True)
    )

    final_video = CompositeVideoClip([clip, text_clip, text_clip_top])
    final_video.write_videofile(output_path)
    logger.info(f"Video created: {output_path}")


def search_image_tool(query: str, num_results: int = 5) -> dict:
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


def download_image_to_tempfile(url: str) -> str:
    """Download remote image to a temp file with .jpg extension."""
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, stream=True, headers=headers)
    response.raise_for_status()

    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
    with open(tmp_file.name, "wb") as f:
        for chunk in response.iter_content(1024):
            f.write(chunk)
    return tmp_file.name


def get_random_mp3_full_path(exclude: str) -> str:
    mp3_files = [
        f
        for f in os.listdir(social_constants.SOUND_TRACK_PATH)
        if f.endswith(".mp3") and f != exclude
    ]
    if not mp3_files:
        return None

    return os.path.join(social_constants.SOUND_TRACK_PATH, random.choice(mp3_files))


def sanity_check_ai_caption(ai_caption: str) -> str:
    ai_caption = ai_caption.replace('"', "")

    reversed_text = ai_caption[::-1]
    match = re.search(r"[.!?]", reversed_text)
    if match:
        cut_index = len(ai_caption) - match.start()
        return ai_caption[:cut_index]
    return ai_caption.strip()


async def notify_social_token_expired(message: str = None):
    conf = ConnectionConfig(
        MAIL_USERNAME="your_email@example.com",
        MAIL_PASSWORD="your_email_password",
        MAIL_FROM="your_email@example.com",
        MAIL_PORT=587,
        MAIL_SERVER="smtp.example.com",
        MAIL_USE_TLS=True,
        MAIL_USE_SSL=False,
    )

    email = MessageSchema(
        subject="Simplified Bites - SOCIAL TOKEN EXPIRED",
        body=message,
        from_email="hello@simplifiedbites.com",
        to=["joaquinpunales@gmail.com"],
        reply_to=["hello@simplifiedbites.com"],
    )

    email.content_subtype = "html"
    try:
        fm = FastMail(conf)
        await fm.send_message(message)
    except Exception as e:
        print(f"Error sending email: {e}")
