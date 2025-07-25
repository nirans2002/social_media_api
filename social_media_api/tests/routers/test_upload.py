import contextlib
import os
import pathlib
import tempfile

import pytest
from httpx import AsyncClient



# Add a sample image to the fake filesystem
@pytest.fixture()
def sample_image(fs) -> pathlib.Path:
    path = (pathlib.Path(__file__).parent / "assets" / "myfile.png").resolve()
    fs.create_file(path)
    return path


# Mock the b2_upload_file function so that it returns a fake URL
@pytest.fixture(autouse=True)
def mock_b2_upload_file(mocker):
    return mocker.patch(
        "social_media_api.routers.upload.b2_upload_file", return_value="https://fakeurl.com"
    )


# Mock the aiofiles.open function so that it
# returns a fake file object from the fake filesystem
@pytest.fixture(autouse=True)
def aiofiles_mock_open(mocker, fs):
    mock_open = mocker.patch("aiofiles.open")

    @contextlib.asynccontextmanager
    async def async_file_open(fname: str, mode: str = "r"):
        out_fs_mock = mocker.AsyncMock(name=f"async_file_open:{fname!r}/{mode!r}")
        with open(fname, mode) as fin:
            out_fs_mock.read.side_effect = fin.read
            out_fs_mock.write.side_effect = fin.write
            yield out_fs_mock

    mock_open.side_effect = async_file_open
    return mock_open


async def call_upload_endpoint(
    async_client: AsyncClient, token: str, sample_image: pathlib.Path
):
    return await async_client.post(
        "/upload",
        files={"file": open(sample_image, "rb")},
        headers={"Authorization": f"Bearer {token}"},
    )


@pytest.mark.anyio
async def test_upload_image(
    async_client: AsyncClient, logged_in_token: str, sample_image: pathlib.Path
):
    response = await call_upload_endpoint(async_client, logged_in_token, sample_image)
    assert response.status_code == 201
    assert response.json()["file_url"] == "https://fakeurl.com"


@pytest.mark.anyio
async def test_temp_file_removed_after_upload(
    async_client: AsyncClient, logged_in_token: str, sample_image: pathlib.Path, mocker
):
    # Spy on the NamedTemporaryFile function
    named_temp_file_spy = mocker.spy(tempfile, "NamedTemporaryFile")

    response = await call_upload_endpoint(async_client, logged_in_token, sample_image)
    assert response.status_code == 201

    # Get the filename of the temporary file created by the upload endpoint
    created_temp_file = named_temp_file_spy.spy_return

    # Check if the temp_file is removed after the file is uploaded
    assert not os.path.exists(created_temp_file.name)