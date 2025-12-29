"""Utility functions."""

from datetime import datetime, timedelta
from pathlib import Path


def todays_date() -> str:
    """Get todays date in the Format of YYYY-MM-DD."""
    return datetime.now().date().strftime(r"%Y-%m-%d")


def is_date_within_days(date: str, delta: int) -> bool:
    """Check whether the given date is within `delta` days before today."""
    today = datetime.strptime(todays_date(), r"%Y-%m-%d")
    past_date = datetime.strptime(date, r"%Y-%m-%d")
    return past_date + timedelta(days=delta) >= today


def remove_env_from_path(path: Path) -> Path:
    """Remove .env from a given path."""
    if path.is_file():
        return path.parent
    else:
        return path


def is_env_path_valid(env_path: Path) -> bool:
    """Check whether a given path exists and if it contains a .env file."""
    return env_path.exists() and env_path.is_file() and env_path.name == ".env"
