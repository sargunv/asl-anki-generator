import logging
import os
import time

import requests

from . import DOWNLOAD_INTERVAL


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
) -> str | None:
    """Download a video from HandSpeak.

    Args:
        filename: The local filename (without extension), e.g. "hello" or "how-you".
        url: The full URL to download from.
        force_redownload: If True, re-download even if the file exists locally.

    Returns the relative path of the downloaded video, or None on failure.
    """
    filepath = f"videos/{filename}.mp4"

    if not force_redownload and os.path.isfile(filepath):
        logging.info(f'Sign video "{filepath}" has been previously downloaded; skipping.')
        return filepath

    logging.info(f"Downloading {filepath}...")
    time.sleep(DOWNLOAD_INTERVAL)

    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers, allow_redirects=True)

    if not r.ok:
        logging.warning(f'Error downloading sign video for "{filename}". Please double-check the URL.')
        return None

    logging.info(f'Successfully downloaded "{filepath}"!')

    os.makedirs("videos/", exist_ok=True)
    open(filepath, "wb").write(r.content)
    return filepath
