from unittest.mock import MagicMock, patch

import requests

from aslankigen.util import DownloadStatus, download_sign_video


@patch("aslankigen.util.time.sleep", return_value=None)
@patch("aslankigen.util.requests.get")
class TestDownloadSignVideo:
    """Tests for download_sign_video with mocked HTTP and sleep."""

    def test_cached_file(self, mock_get: MagicMock, mock_sleep: MagicMock, tmp_path):
        """When the file already exists, return (filepath, CACHED) without requesting."""
        cached_file = tmp_path / "hello.mp4"
        cached_file.write_bytes(b"existing content")

        result_path, status = download_sign_video("hello", "https://example.com/hello.mp4", output_dir=tmp_path)

        assert result_path == cached_file
        assert status is DownloadStatus.CACHED
        mock_get.assert_not_called()
        mock_sleep.assert_not_called()

    def test_successful_download(self, mock_get: MagicMock, mock_sleep: MagicMock, tmp_path):
        """A 200 response writes the file and returns (filepath, DOWNLOADED)."""
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.content = b"video bytes"
        mock_get.return_value = mock_response

        result_path, status = download_sign_video("hello", "https://example.com/hello.mp4", output_dir=tmp_path)

        assert result_path is not None
        assert result_path == tmp_path / "hello.mp4"
        assert status is DownloadStatus.DOWNLOADED
        assert result_path.read_bytes() == b"video bytes"
        mock_sleep.assert_called_once()

    def test_failed_download(self, mock_get: MagicMock, mock_sleep: MagicMock, tmp_path):
        """A 404 response returns (None, FAILED)."""
        mock_response = MagicMock()
        mock_response.ok = False
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        result_path, status = download_sign_video("hello", "https://example.com/hello.mp4", output_dir=tmp_path)

        assert result_path is None
        assert status is DownloadStatus.FAILED

    def test_network_error(self, mock_get: MagicMock, mock_sleep: MagicMock, tmp_path):
        """A ConnectionError returns (None, FAILED)."""
        mock_get.side_effect = requests.ConnectionError("no network")

        result_path, status = download_sign_video("hello", "https://example.com/hello.mp4", output_dir=tmp_path)

        assert result_path is None
        assert status is DownloadStatus.FAILED

    def test_force_redownload(self, mock_get: MagicMock, mock_sleep: MagicMock, tmp_path):
        """With force_redownload=True, re-download even when the file exists."""
        cached_file = tmp_path / "hello.mp4"
        cached_file.write_bytes(b"old content")

        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.content = b"new content"
        mock_get.return_value = mock_response

        result_path, status = download_sign_video(
            "hello",
            "https://example.com/hello.mp4",
            force_redownload=True,
            output_dir=tmp_path,
        )

        assert result_path == cached_file
        assert status is DownloadStatus.DOWNLOADED
        assert cached_file.read_bytes() == b"new content"
        mock_get.assert_called_once()

    def test_timeout_set(self, mock_get: MagicMock, mock_sleep: MagicMock, tmp_path):
        """requests.get is called with timeout=30."""
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.content = b"data"
        mock_get.return_value = mock_response

        download_sign_video("hello", "https://example.com/hello.mp4", output_dir=tmp_path)

        _, kwargs = mock_get.call_args
        assert kwargs["timeout"] == 30
