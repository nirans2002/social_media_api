import pytest
from jose import jwt

from social_media_api import security

@pytest.mark.anyio
async def test_get_user(registered_user: dict):
    user = await security.get_user(registered_user["email"])

    assert user.email == registered_user["email"]

@pytest.mark.anyio
async def test_get_user_not_found():
    user = await security.get_user("test@email.com")
    assert user is None

def test_password_hashes():
    password = "test_password"
    assert security.verify_password(password, security.get_password_hash(password))