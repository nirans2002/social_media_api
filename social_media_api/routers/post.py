import logging
from typing import Annotated
import sqlalchemy
from enum import Enum
from fastapi import Depends, APIRouter, HTTPException, Request
from social_media_api.database import database,post_table,comment_table, likes_table
from social_media_api.models.post import (
    UserPost,
    UserPostIn,
    Comment,
    CommentIn,
    UserPostWithComments,
    UserPostWithLikes,
    PostLike,
    PostLikeIn
)
from social_media_api.models.user import User
from social_media_api.security import get_current_user,oauth2_scheme

router = APIRouter()

logger = logging.getLogger(__name__)
# post_table = {}
# comment_table = {}


select_post_and_likes = (
    sqlalchemy.select(post_table, sqlalchemy.func.count(likes_table.c.id).label("likes"))
    .select_from(post_table.outerjoin(likes_table))
    .group_by(post_table.c.id)
)

class PostSorting(str, Enum):
    new = "new"
    old = "old"
    most_likes = "most_likes"


async def find_post(post_id: int):
    query = post_table.select().where(post_table.c.id==post_id)
    return await database.fetch_one(query)


#  create post
@router.post("/post", response_model=UserPost, status_code=201)
async def create_post(post: UserPostIn, current_user: Annotated[User,Depends(get_current_user)]):
    data = {**post.model_dump(), "user_id": current_user.id}
    query = post_table.insert().values(data)
    last_record_id = await database.execute(query)
    return {**data, "id": last_record_id}


# get all posts
@router.get("/posts", response_model=list[UserPostWithLikes])
async def get_all_posts(sorting : PostSorting = PostSorting.new):
    if sorting == PostSorting.new:
        query = select_post_and_likes.order_by(post_table.c.id.desc())
    if sorting == PostSorting.old:
        query = select_post_and_likes.order_by(post_table.c.id.asc())
    if sorting == PostSorting.most_likes:
        query = select_post_and_likes.order_by(sqlalchemy.desc("likes"))
    logger.debug(query)
    return await database.fetch_all(query)


# create comments
@router.post("/comment", response_model=Comment, status_code=201)
async def create_comment(comment: CommentIn,current_user: Annotated[User,Depends(get_current_user)]):
    post = await find_post(comment.post_id)
    if not post:
        # logger.error(f"post with id {comment.post_id} not found")
        raise HTTPException(status_code=404, detail="post not found")
    data = {**comment.model_dump(), "user_id": current_user.id}
    query = comment_table.insert().values(data)
    last_record_id = await database.execute(query)
    return {**data, "id": last_record_id}


# get comments of a given post
@router.get("/post/{post_id}/comment", response_model=list[Comment])
async def get_comment_on_post(post_id: int):
    query = comment_table.select().where(comment_table.c.post_id == post_id)
    return await database.fetch_all(query)


# get post with comments
@router.get("/post/{post_id}", response_model=UserPostWithComments)
async def get_post_with_comments(post_id: int):
    # post  = await find_post(post_id)
    query = select_post_and_likes.where(post_table.c.id == post_id)
    post =  await database.fetch_one(query)
    if not post:
        # logger.error(f"post id {post_id} not found")
        raise HTTPException(status_code=404,detail="post not found")
    return {
        "post" : post,
        "comments": await get_comment_on_post(post_id)
    }


@router.post("/like",response_model=PostLike, status_code=201)
async def like_post(
    like: PostLikeIn,
    current_user: Annotated[User,Depends(get_current_user)]
):
    logger.info("like post")
    post = await find_post(like.post_id)

    if not post:
        # logger.error(f"post id {post_id} not found")
        raise HTTPException(status_code=404,detail="post not found")
    data = {**like.model_dump(), "user_id": current_user.id}
    query = likes_table.insert().values(data)
    logger.debug(query)
    last_record_id = await database.execute(query)
    return {**data, "id": last_record_id}