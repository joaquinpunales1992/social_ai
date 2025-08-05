from fastapi import FastAPI
from social.facebook.routes import router as facebook_router
from social.instagram.routes import router as instagram_rotuer

app = FastAPI()

app.include_router(facebook_router)
app.include_router(instagram_rotuer)
