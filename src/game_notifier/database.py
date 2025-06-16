"""Basic data persistance."""

import sqlite3
from pathlib import Path
from . import utils


def get_db_connection(path: Path) -> sqlite3.Connection:
    """Get DB connection for use in with statement."""
    return sqlite3.connect(path.joinpath('data.db'))


def sqlite_get_steam_game(path: Path, game_id: int):
    """Get an entry from sqlite for Steam.

    Returns:
        tuple of (game_id, last_notified)

    """
    with get_db_connection(path) as conn:
        cursor = conn.cursor()
        query = 'SELECT game_id, last_notified FROM SteamSale WHERE game_id = ?;'
        return cursor.execute(query, (game_id,)).fetchone()


def sqlite_set_or_update_steam_game(path: Path, game_id: int, date: str):
    """Set an entry from sqlite for Steam or update last_notified if already exists."""
    with get_db_connection(path) as conn:
        cursor = conn.cursor()
        query = (
            'INSERT OR REPLACE INTO SteamSale (game_id, last_notified) VALUES (?, ?);'
        )
        cursor.execute(query, (game_id, date))


def sqlite_add_steam_game(path: Path, game_id: int):
    """Add a new entry into sqlite for Steam."""
    date_today = utils.todays_date()
    with get_db_connection(path) as conn:
        cursor = conn.cursor()
        query = 'INSERT INTO SteamSale (game_id, last_notified) VALUES (?, ?);'
        cursor.execute(query, (game_id, date_today))
    print(f'added Steam game {game_id} to DB')


def sqlite_get_epic_entry(path: Path, title: str):
    """Get an entry from sqlite for Epic games notification.

    Returns:
        tuple of (title, date_notified)

    """
    with get_db_connection(path) as conn:
        cursor = conn.cursor()
        query = 'SELECT title, date_notified FROM EpicNotification WHERE title = ?;'
        return cursor.execute(query, (title,)).fetchone()


def sqlite_set_epic_entry(path: Path, title: str, date_notified: str):
    """Set an entry for EpicNotification or update date_notified if already exists."""
    with get_db_connection(path) as conn:
        cursor = conn.cursor()
        query = 'INSERT INTO EpicNotification (title, date_notified) VALUES (?, ?);'
        cursor.execute(query, (title, date_notified))


def init_sqlite_db(path: Path):
    """Initialize database.

    :param Path path: A path to users working directory WITHOUT the filename.
    """
    with get_db_connection(path) as conn:
        cursor = conn.cursor()
        steam_table = """
            CREATE TABLE IF NOT EXISTS SteamSale (
                game_id INTEGER PRIMARY KEY NOT NULL,
                last_notified TEXT
            );
        """
        epic_table = """
            CREATE TABLE IF NOT EXISTS EpicNotification (
                title TEXT PRIMARY KEY NOT NULL,
                date_notified TEXT
            );
        """
        cursor.execute(steam_table)
        cursor.execute(epic_table)
    print('SETUP: database initialized')
