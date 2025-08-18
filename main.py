from fastapi import FastAPI
from social.facebook.routes import router as facebook_router
from social.instagram.routes import router as instagram_rotuer
from social.youtube.routes import router as youtube_router

app = FastAPI(
    title="SocialAI API",
    version="1.0.0",
    contact={
        "name": "API Support",
        "email": "hello@akiyainjapan.com",
    }
    )

app.include_router(facebook_router)
app.include_router(instagram_rotuer)
app.include_router(youtube_router)
