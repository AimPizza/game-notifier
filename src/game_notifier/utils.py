"""Small utilities for more complex calculations."""

from datetime import datetime, timedelta
from pathlib import Path
from . import database


def todays_date() -> str:
    """Get todays date in the Format of YYYY-MM-DD."""
    return datetime.now().date().strftime(r'%Y-%m-%d')


def is_date_within_days(date: str, delta: int) -> bool:
    """Check whether the given date is within `delta` days before today."""
    today = datetime.strptime(todays_date(), r'%Y-%m-%d')
    past_date = datetime.strptime(date, r'%Y-%m-%d')
    return past_date + timedelta(days=delta) >= today


def steam_should_notify(working_dir: Path, game_id: int) -> bool:
    """Check whether the given Steam game is eligible for a notification.

    What makes a game illegible?
    - notification already happened within a certain timeframe
    """
    data = database.sqlite_get_steam_game(working_dir, game_id)
    if data is None:
        # If no record exists, we can assume that the user was not notified before
        return True
    _, last_notified = data
    if is_date_within_days(last_notified, 7):
        return False
    return True


def epic_should_notify(working_dir: Path, title: str) -> bool:
    """Check whether the given EpicGames game is eligible for a notification.

    What makes a game illegible?
    - notification already happened for that game (your loss if you missed to claim it)
    """
    data = database.sqlite_get_epic_entry(working_dir, title)
    if data is None:
        return True
    return False


def remove_env_from_path(path: Path) -> Path:
    """Remove .env from a given path."""
    if path.is_file():
        return path.parent
    else:
        return path


def is_env_path_valid(env_path: Path) -> bool:
    """Check whether a given path exists and if it contains a .env file."""
    if env_path.exists() and env_path.is_file() and '.env' in env_path.name:
        return True
    else:
        return False
