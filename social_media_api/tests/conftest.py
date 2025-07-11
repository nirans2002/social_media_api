import os
from typing import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from httpx import ASGITransport
# from httpx import AsyncClient
os.environ["ENV_STATE"] = "test"

from social_media_api.routers.post import comment_table, post_table

from social_media_api.database import database
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
