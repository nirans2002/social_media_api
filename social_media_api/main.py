from asgi_correlation_id import CorrelationIdMiddleware
from contextlib import asynccontextmanager
from fastapi import FastAPI,HTTPException
from fastapi.exception_handlers import http_exception_handler
from social_media_api.database import database
from social_media_api.routers.post import router as post_router
from social_media_api.logger_config import configure_logging
from social_media_api.routers.user import router as user_router
from social_media_api.routers.upload import router as upload_router
import logging

logger = logging.getLogger(__name__)
@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    logger.info("application started")
    await database.connect()
    logger.info(f"database connected {database.url}")
    yield
    await database.disconnect()

app = FastAPI(lifespan=lifespan)
app.add_middleware(CorrelationIdMiddleware)


app.include_router(post_router)
app.include_router(user_router)
app.include_router(upload_router)


@app.exception_handler(HTTPException)
async def handle_exception(request, exception):
    logger.error(f"HTTPException: {exception.status_code} {exception.detail}")
    return await http_exception_handler(request, exception)