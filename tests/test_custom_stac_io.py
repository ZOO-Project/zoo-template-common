from unittest.mock import MagicMock, patch

import pytest
from pystac.stac_io import DefaultStacIO


@pytest.fixture
def stac_io():
    with patch("botocore.session.Session") as mock_session_cls:
        mock_client = MagicMock()
        mock_session_cls.return_value.create_client.return_value = mock_client
        from zoo_template_common.custom_stac_io import CustomStacIO

        yield CustomStacIO()


def test_read_text_s3_url_calls_s3_client(stac_io):
    stac_io.s3_client.get_object.return_value = {
        "Body": MagicMock(read=lambda: b"stac content")
    }
    result = stac_io.read_text("s3://my-bucket/path/to/file.json")
    stac_io.s3_client.get_object.assert_called_once_with(
        Bucket="my-bucket", Key="path/to/file.json"
    )
    assert result == "stac content"


def test_read_text_non_s3_url_delegates_to_default(stac_io):
    with patch.object(DefaultStacIO, "read_text", return_value="local content"):
        result = stac_io.read_text("http://example.com/stac.json")
    assert result == "local content"


def test_write_text_s3_url_calls_put_object(stac_io):
    stac_io.write_text(
        "s3://my-bucket/path/output.json", '{"type": "FeatureCollection"}'
    )
    stac_io.s3_client.put_object.assert_called_once_with(
        Body=b'{"type": "FeatureCollection"}',
        Bucket="my-bucket",
        Key="path/output.json",
        ContentType="application/geo+json",
    )


def test_write_text_non_s3_url_delegates_to_default(stac_io):
    with patch.object(DefaultStacIO, "write_text") as mock_write:
        stac_io.write_text("file:///tmp/output.json", "content")
    mock_write.assert_called_once()


def test_s3_key_strips_leading_slash(stac_io):
    stac_io.s3_client.get_object.return_value = {
        "Body": MagicMock(read=lambda: b"data")
    }
    stac_io.read_text("s3://bucket/prefix/file.json")
    call_kwargs = stac_io.s3_client.get_object.call_args
    assert call_kwargs.kwargs["Key"] == "prefix/file.json"
    # Key must not start with '/'
    assert not call_kwargs.kwargs["Key"].startswith("/")
