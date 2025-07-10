from fastapi import FastAPI
from social_media_api.routers.post import router as post_router

app = FastAPI()

app.include_router(post_router)