"""
Handles notifications sent to users
"""

from datetime import datetime
from pathlib import Path
import time
import requests

from game_notifier.sources import EpicSource, SteamSource
from game_notifier.sources.base import GameStoreSource


def send_ntfy(topic: str, message: str, image_url: str = "", store_url: str = ""):
    """uses ntfy with a valid topic to send out a notification

    :param str topic: url with protocol and path to a ntfy topic
    :param str message: content of the notification
    :param str image_url: url to a valid image (jpg, png, ...)
    :param str store_url: url to store page or place to claim
    """
    headers = {}
    if image_url:
        headers["Attach"] = image_url
    if store_url:
        headers["Actions"] = f"view, store page, {store_url}"

    requests.post(topic, data=message.encode(encoding="utf-8"), headers=headers)


def loop(
    topic: str,
    poll_interval: int,
    notify_epic: bool,
    steam_game_ids: list[int],
    working_dir: Path,
):
    """Execute program logic after everything is set up."""
    while True:
        sources: list[GameStoreSource] = []
        if notify_epic:
            sources.append(EpicSource())
        if steam_game_ids:
            sources.append(SteamSource(steam_game_ids))

        for source in sources:
            for notification in source.poll(working_dir):
                print(f"sending notification for {source.name}:", notification.message)
                send_ntfy(
                    topic,
                    notification.message,
                    image_url=notification.image_url,
                    store_url=notification.store_url,
                )

        print(
            f"done, next iteration in {poll_interval}min, time now is:",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
        time.sleep(poll_interval * 60)
