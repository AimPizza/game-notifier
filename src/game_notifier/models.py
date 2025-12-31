"""Data models used across the project."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class EpicGame:
    title: str = ""
    banner_url: str = ""
    store_url: str = ""


@dataclass(frozen=True, slots=True)
class SteamSaleHit:
    appid: int
    discount_percentage: int
    title: str = ""
    banner_url: str = ""
    store_url: str = ""
    price: str = ""
