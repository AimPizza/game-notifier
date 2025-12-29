"""Store/source abstractions for fetching games and tracking notifications."""

from .base import GameStoreSource, Notification
from .epic import EpicSource
from .steam import SteamSource
