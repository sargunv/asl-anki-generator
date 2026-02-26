import enum
import os
import time

import requests

from . import DOWNLOAD_INTERVAL, console


class DownloadStatus(enum.Enum):
    CACHED = "cached"
    DOWNLOADED = "downloaded"
    FAILED = "failed"


def get_handspeak_path(word: str) -> str:
    """Build the HandSpeak URL path for a standard dictionary word.

    This handles the two known URL patterns:
    - Single letters: /word/{letter}/{letter}-abc.mp4
    - Regular words: /word/{first_char}/{first_3_chars}/{word}.mp4
    """
    if len(word) == 1 and word.isalpha():
        return f"/word/{word}/{word}-abc.mp4"
    return f"/word/{word[:1]}/{word[:3]}/{word}.mp4"


def download_sign_video(
    filename: str,
    url: str,
    force_redownload: bool = False,
) -> tuple[str | None, DownloadStatus]:
    """Download a video from HandSpeak.

    Args:
        filename: The local filename (without extension), e.g. "hello" or "how-you".
        url: The full URL to download from.
        force_redownload: If True, re-download even if the file exists locally.

    Returns a (filepath, status) tuple. filepath is None on failure.
    """
    filepath = f"videos/{filename}.mp4"

    if not force_redownload and os.path.isfile(filepath):
        return filepath, DownloadStatus.CACHED

    time.sleep(DOWNLOAD_INTERVAL)

    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers, allow_redirects=True)

    if not r.ok:
        console.print(f"  [bold red]Failed[/bold red] {filename} [dim]({r.status_code})[/dim]")
        return None, DownloadStatus.FAILED

    os.makedirs("videos/", exist_ok=True)
    open(filepath, "wb").write(r.content)

    console.print(f"  [green]Downloaded[/green] {filepath}")
    return filepath, DownloadStatus.DOWNLOADED
