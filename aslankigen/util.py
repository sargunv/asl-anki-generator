import enum
import time
from pathlib import Path

import requests

from . import DOWNLOAD_INTERVAL, console

VIDEOS_DIR = Path("videos")


class DownloadStatus(enum.Enum):
    CACHED = "cached"
    DOWNLOADED = "downloaded"
    FAILED = "failed"


def download_sign_video(
    filename: str,
    url: str,
    *,
    force_redownload: bool = False,
    output_dir: Path = VIDEOS_DIR,
) -> tuple[Path | None, DownloadStatus]:
    """Download a video from HandSpeak.

    Args:
        filename: The local filename (without extension), e.g. "hello" or "how-you".
        url: The full URL to download from.
        force_redownload: If True, re-download even if the file exists locally.
        output_dir: Directory to save videos to.

    Returns a (filepath, status) tuple. filepath is None on failure.
    """
    filepath = output_dir / f"{filename}.mp4"

    if not force_redownload and filepath.is_file():
        return filepath, DownloadStatus.CACHED

    time.sleep(DOWNLOAD_INTERVAL)

    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, allow_redirects=True, timeout=30)
    except requests.RequestException as exc:
        console.print(f"  [bold red]Failed[/bold red] {filename} [dim]({exc})[/dim]")
        return None, DownloadStatus.FAILED

    if not r.ok:
        console.print(f"  [bold red]Failed[/bold red] {filename} [dim]({r.status_code})[/dim]")
        return None, DownloadStatus.FAILED

    output_dir.mkdir(parents=True, exist_ok=True)
    filepath.write_bytes(r.content)

    console.print(f"  [green]Downloaded[/green] {filepath}")
    return filepath, DownloadStatus.DOWNLOADED
