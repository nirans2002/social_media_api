import logging

from social_media_api.database import database, user_table
from passlib.context import CryptContext


logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"])


def get_password_hash (password:str) -> str:
    return pwd_context.hash(password)


def verify_password(password:str,hash_password) -> bool:
    return pwd_context.verify(password,hash=hash_password)

async def get_user(email:str):
    logger.debug("fectching user from db",extra= {"email":email})
    query = user_table.select().where(user_table.c.email ==email)
    result = await database.fetch_one(query)
    if result:
        return result
    