import os
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, Mock
import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport
# from httpx import AsyncClient
from httpx import AsyncClient, Request, Response

os.environ["ENV_STATE"] = "test"

from social_media_api.routers.post import comment_table, post_table

from social_media_api.database import database,user_table
from social_media_api.main import app

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture()
def client() -> Generator:
    yield TestClient(app)


@pytest.fixture(autouse=True)
async def db() -> AsyncGenerator:
    await database.connect()
    print(f"database : {database.url}")
    yield
    await database.disconnect()


@pytest.fixture()
# @pytest.fixture()
async def async_client() -> AsyncGenerator:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac


@pytest.fixture()
async def registered_user(async_client: AsyncClient) -> dict:
    user_details = {"email": "test@example.net", "password": "1234"}
    await async_client.post("/register", json=user_details)
    query = user_table.select().where(user_table.c.email == user_details["email"])
    user = await database.fetch_one(query)
    user_details["id"] = user.id
    return user_details

@pytest.fixture()
async def logged_in_token(async_client: AsyncClient, confirmed_user: dict) -> str:
    response = await async_client.post("/token", json=confirmed_user)
    print(response.json())
    return response.json()["access_token"]

@pytest.fixture()
async def confirmed_user(registered_user: dict) -> dict:
    query = (
        user_table.update()
        .where(user_table.c.email == registered_user["email"])
        .values(confirmed=True)
    )
    await database.execute(query)
    return registered_user



# @pytest.fixture(autouse=True)
# def mock_httpx_client(mocker):
#     """
#     Fixture to mock the HTTPX client so that we never make any
#     real HTTP requests (especially important when registering users).
#     """
#     mocked_client = mocker.patch("social_media_api.tasks.httpx.AsyncClient")

#     mocked_async_client = Mock()
#     response = Response(status_code=200, content="", request=Request("POST", "//"))
#     mocked_async_client.post = AsyncMock(return_value=response)
#     mocked_client.return_value.__aenter__.return_value = mocked_async_client

#     return mocked_async_client