from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    cerebras_api_key: str = Field(..., env="CEREBRAS_API_KEY")
    facebook_page_id: str = Field(..., env="FACEBOOK_PAGE_ID")
    use_ai_caption: bool = Field(default=True)
    meta_access_token: str = Field(..., env="META_ACCESS_TOKEN")
    google_api_key: str = Field(..., env="GOOGLE_API_KEY")
    google_cse_id: str = Field(..., env="GOOGLE_CSE_ID")
    instagram_page_id: str = Field(..., env="INSTAGRAM_PAGE_ID")

    class Config:
        env_file = ".env"


settings = Settings()
