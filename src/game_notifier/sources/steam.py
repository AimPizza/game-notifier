"""Steam source implementation."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from game_notifier import database, fetcher, utils
from game_notifier.models import SteamSaleHit

from .base import GameStoreSource, Notification


class SteamSource(GameStoreSource[SteamSaleHit]):
    name = "steam"

    def __init__(self, wanted_game_ids: list[int]):
        self._wanted_game_ids = wanted_game_ids

    def fetch(self) -> Iterable[SteamSaleHit]:
        hits: list[SteamSaleHit] = []
        for appid in self._wanted_game_ids:
            sale_hit = fetcher.steam_sale(appid)
            if sale_hit:
                hits.append(sale_hit)
        return hits

    def item_key(self, item: SteamSaleHit) -> str:
        return str(item.appid)

    def should_notify(self, working_dir: Path, key: str) -> bool:
        last_notified = database.sqlite_get_notification(
            working_dir, source=self.name, key=key
        )
        if last_notified is None:
            return True
        return not utils.is_date_within_days(last_notified, 7)

    def to_notification(self, item: SteamSaleHit) -> Notification:
        message = (
            f"{item.title} is on sale for {item.price}! (-{item.discount_percentage}%)"
        )
        return Notification(message=message, image_url=item.banner_url)
