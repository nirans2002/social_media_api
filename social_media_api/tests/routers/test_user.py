from httpx import AsyncClient
import pytest


async def register_user(async_client : AsyncClient,email:str,password:str):
    return await async_client.post("/register", json={
        "email":email, "password":password
    })

@pytest.mark.anyio
async def test_register_user(async_client : AsyncClient):
    response = await register_user(async_client,"testuser@email.com","test_usr_psswrd")
    assert response.status_code == 201
    assert "user created" in response.json()["detail"]



@pytest.mark.anyio
async def test_register_user_already_exitss(async_client : AsyncClient, registered_user : dict):
    response = await register_user(async_client,registered_user["email"],registered_user["password"])
    assert response.status_code == 400
    assert "exists" in response.json()["detail"]