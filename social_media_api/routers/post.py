from fastapi import APIRouter, HTTPException
from social_media_api.database import database,post_table,comment_table
from social_media_api.models.post import (
    UserPost,
    UserPostIn,
    Comment,
    CommentIn,
    UserPostWithComments,
)

router = APIRouter()


# post_table = {}
# comment_table = {}


async def find_post(post_id: int):
    query = post_table.select().where(post_table.c.id==post_id)
    return await database.fetch_one(query)


#  create post
@router.post("/post", response_model=UserPost, status_code=201)
async def create_post(post: UserPostIn):
    data = post.model_dump()  
    query = post_table.insert().values(data)
    last_record_id = await database.execute(query)
    return {**data, "id": last_record_id}


# get all posts
@router.get("/posts", response_model=list[UserPost])
async def get_all_posts():
    query = post_table.select()
    return await database.fetch_all(query)


# create comments
@router.post("/comment", response_model=Comment, status_code=201)
async def create_comment(comment: CommentIn):
    post = await find_post(comment.post_id)
    if not post:
        raise HTTPException(status_code=404, detail="post not found")
    data = comment.model_dump()  # previously .dict()
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
    post  = await find_post(post_id)
    if not post:
        raise HTTPException(status_code=404,detail="post not found")
    return {
        "post" : post,
        "comments": await get_comment_on_post(post_id)
    }
