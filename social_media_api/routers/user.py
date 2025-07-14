from fastapi import APIRouter, BackgroundTasks, HTTPException, status, Form, Depends,Request
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from social_media_api.models.user import UserIn
from social_media_api import tasks
from social_media_api.security import authenticate_user, get_user,get_password_hash,create_access_token,get_subject_for_token_type,create_confirm_token
from social_media_api.database import user_table,database
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/register",status_code=201)
async def register(user:UserIn,request:Request,background_tasks:BackgroundTasks):
    if await get_user(user.email):
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "user already exists"
        )
    hashed_password = get_password_hash(user.password)
    query = user_table.insert().values(email = user.email, password = hashed_password)
    logger.debug(query)

    await database.execute(query)
    background_tasks.add_task(
        tasks.send_user_registration_email,
        user.email, confirmation_url= request.url_for(
            "confirm_email", token=create_confirm_token(user.email)
        ),
    )
    return {
        "detail": "User created. Please confirm your email.",
        "confirmation_url": request.url_for(
            "confirm_email", token=create_confirm_token(user.email)
        ),
    }



# @router.post("/token")
# async def login(
#     form_data : Annotated[OAuth2PasswordRequestForm, Depends()]
#     ):
#     user = await authenticate_user(form_data.username,form_data.password)
#     access_token = create_access_token(user.email)
#     return {
#         "access_token":access_token,
#         "token_type": "bearer"
#     }


@router.post("/token")
async def login(user:UserIn):
    user = await authenticate_user(user.email,user.password)
    access_token = create_access_token(user.email)
    return {
        "access_token":access_token,
        "token_type": "bearer"
     }



@router.get("/confirm/{token}")
async def confirm_email(token: str):
    email = get_subject_for_token_type(token, "confirmation")
    query = (
        user_table.update().where(user_table.c.email == email).values(confirmed=True)
    )

    logger.debug(query)

    await database.execute(query)
    return {"detail": "User confirmed"}