from ai.cerebras import CerebrasAI
import logging
import json
from social.models import SocialPost
from social.ai.tools import (
    tools,
    post_on_instagram_tool,
    reel_on_instagram_tool,
    search_image_tool,
    available_properties_to_post,
)
from social.instagram.utils import publish_instagram_post, publish_instagram_reel
from social.facebook.utils import publish_facebook_post, publish_facebook_reel


logger = logging.getLogger(__name__)


class AIAnalyst:
    def __init__(self):
        self.cerebras_ai_client = CerebrasAI()

    def get_social_posts(self):
        return SocialPost.objects.all().values(
            "caption", "datetime", "social_media", "content_type"
        )

    def get_available_properties(self):
        return [
            {"id": 1, "title": "Beatiful House in Tokyo", "price": 12000, "bedrooms": 3},
            {"id": 2, "title": "Beatiful House in Kyoto", "price": 24000, "bedrooms": 5},
            {"id": 3, "title": "Beatiful House in Osaka", "price": 19000, "bedrooms": 5},
        ]
    

    def already_posted(self):
        return [
            {"title": "House Tokyo", "price": 15000, "bedrooms": 3},
            {"title": "Beatiful House in Tokyo", "price": 24000, "bedrooms": 5},
        ]

    def analyze_content_to_post(self):
        messages = [
            {
                "role": "system",
                "content": "You are a helpful Community Manager,"
                " that manages social media for a page that sells Houses in Japan,"
                " you have access to mulitple tools: reel_on_facebook_tool, post_on_facebook_tool, available_properties_to_post\n\n "
                f" You have already posted {self.get_social_posts()} \n\n"
                f" You have available this properties to post content about: {self.get_available_properties()} \n\n"
                " Use the tools when you think is a good moment to publish a post or publish a reel on facebook.",
            },
            {
                "role": "user",
                "content": "Given the details you have, decide if you should post a facebook reel or an facebook post, which post, etc. \n\n"
                "Given the tools you have available: post_on_facebook_tool, reel_on_facebook_tool and available_properties_to_post",
            },
        ]
        import pdb

        pdb.set_trace()
        cerebras_ai_client = CerebrasAI()
        response = cerebras_ai_client.generate_with_tools(
            messages=messages, tools=tools
        )
        choice = response.choices[0].message

        if choice.tool_calls:
            for tool_call in choice.tool_calls:
                name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)

                if name == "post_on_instagram_tool":
                    result = post_on_instagram_tool(
                        property_id=arguments["property_id"],
                        caption=arguments["caption"],
                    )
                elif name == "reel_on_instagram_tool":
                    result = reel_on_instagram_tool(
                        property_id=arguments["property_id"],
                        caption=arguments["caption"],
                    )
                elif name == "search_image_tool":
                    result = search_image_tool(
                        query=arguments.get("query"),
                        num_results=arguments.get("num_results"),
                    )
                elif name == "available_properties_to_post":
                    result = available_properties_to_post()

                else:
                    logger.warning(f"Unknown tool: {name}")
                    continue

                # Feed result back
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result),
                    }
                )

            # Re-generate final response
            final_response = cerebras_ai_client.generate_text(
                model="llama-4-scout-17b-16e-instruct",
                messages=messages,
            )
            if final_response:
                logger.info(
                    "Final model output: %s", final_response.choices[0].message.content
                )
        else:
            logger.error("No tool calls in the response.")

    def publish_instagram_reel(self):
        prompt_system = "You are a helpful Community Manager that manages social media for a page that sells Houses in Japan \n\n"
        prompt_user = "Decide which post you'll be posting. Return the property selected in item_id, Create the caption, the top video text and the label text to use in the video reel. \n\n"
        f"You have this properties available: {self.get_available_properties} \n\n"
        f"You have already posted: {self.already_posted}"
        
        response = self.cerebras_ai_client.generate_content_for_facebook_reel(
            prompt_system=prompt_system,
            prompt_user=prompt_user,
        )

        import pdb

        pdb.set_trace()

        # publish_facebook_reel(
        #     content_data=content_data,
        #     image_urls=image_urls,
        #     hashtags=hashtags,
        #     default_caption=default_caption,
        #     facebook_page_id=FACEBOOK_PAGE_ID,
        #     use_ai_caption=True,
        #     last_reel_posted_sound_track=last_caption_generated,
        #     last_caption_generated=last_caption_generated,
        #     video_text=video_text,
        # )
