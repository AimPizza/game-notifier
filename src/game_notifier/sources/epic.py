"""Epic Games source implementation."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from game_notifier import database, fetcher
from game_notifier.models import EpicGame

from .base import GameStoreSource, Notification


class EpicSource(GameStoreSource[EpicGame]):
    name = "epic"

    def fetch(self) -> Iterable[EpicGame]:
        return fetcher.epic_free_games()

    def item_key(self, item: EpicGame) -> str:
        return item.title

    def should_notify(self, working_dir: Path, key: str) -> bool:
        return (
            database.sqlite_get_notification(working_dir, source=self.name, key=key)
            is None
        )

    def to_notification(self, item: EpicGame) -> Notification:
        return Notification(
            message=f"{item.title} is currently free on Epic Games!",
            image_url=item.banner_url,
        )
