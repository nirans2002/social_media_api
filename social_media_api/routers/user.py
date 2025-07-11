from fastapi import APIRouter, HTTPException, status
from social_media_api.models.user import UserIn
from social_media_api.security import get_user
from social_media_api.database import user_table,database
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/register",status_code=201)
async def register(user:UserIn):
    if await get_user(user.email):
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "user already exists"
        )
    
    query = user_table.insert().value(email = user.email, password = user.password)
    logger.debug(query)

    await database.execute(query)
    return {"detail":"user created"}