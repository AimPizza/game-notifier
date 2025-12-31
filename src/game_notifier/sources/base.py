"""Base classes for game sources."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Generic, Iterable, TypeVar

from game_notifier import database, utils


@dataclass(frozen=True, slots=True)
class Notification:
    message: str
    image_url: str = ""
    store_url: str = ""


TItem = TypeVar("TItem")


class GameStoreSource(ABC, Generic[TItem]):
    """Common interface for a store that can produce notifications."""

    name: str

    @abstractmethod
    def fetch(self) -> Iterable[TItem]:
        raise NotImplementedError

    @abstractmethod
    def item_key(self, item: TItem) -> str:
        raise NotImplementedError

    @abstractmethod
    def to_notification(self, item: TItem) -> Notification:
        raise NotImplementedError

    @abstractmethod
    def should_notify(self, working_dir: Path, key: str) -> bool:
        raise NotImplementedError

    def save_notified(self, working_dir: Path, key: str) -> None:
        database.sqlite_set_notification(
            working_dir, source=self.name, key=key, last_notified=utils.todays_date()
        )

    def poll(self, working_dir: Path) -> Iterable[Notification]:
        for item in self.fetch():
            key = self.item_key(item)
            if self.should_notify(working_dir, key):
                self.save_notified(working_dir, key)
                yield self.to_notification(item)
