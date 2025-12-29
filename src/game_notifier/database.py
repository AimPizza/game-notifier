"""Basic data persistance."""

import sqlite3
from pathlib import Path
from typing import Optional

from game_notifier.models import EpicGame

from . import utils


def get_db_connection(path: Path) -> sqlite3.Connection:
    """Get DB connection for use in with statement."""
    return sqlite3.connect(path.joinpath("data.db"))


def _table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    cursor = conn.cursor()
    query = "SELECT 1 FROM sqlite_master WHERE type='table' AND name = ?;"
    return cursor.execute(query, (table_name,)).fetchone() is not None


def sqlite_get_notification(path: Path, source: str, key: str) -> Optional[str]:
    """Get a last_notified value for a given (source, key).

    Returns:
        last_notified (YYYY-MM-DD) or None if not present.
    """
    with get_db_connection(path) as conn:
        cursor = conn.cursor()
        query = (
            "SELECT last_notified FROM Notifications "
            "WHERE source = ? AND entry_key = ?;"
        )
        row = cursor.execute(query, (source, key)).fetchone()
        return row[0] if row else None


def sqlite_set_notification(
    path: Path, source: str, key: str, last_notified: str
) -> None:
    """Insert or update a (source, key) notification entry."""
    with get_db_connection(path) as conn:
        cursor = conn.cursor()
        query = (
            "INSERT INTO Notifications (source, entry_key, last_notified) "
            "VALUES (?, ?, ?) "
            "ON CONFLICT(source, entry_key) DO UPDATE SET "
            "last_notified = excluded.last_notified;"
        )
        cursor.execute(query, (source, key, last_notified))


def sqlite_get_steam_game(path: Path, game_id: int):
    """Get an entry from sqlite for Steam.

    Returns:
        tuple of (game_id, last_notified)

    """
    last_notified = sqlite_get_notification(path, source="steam", key=str(game_id))
    if last_notified is None:
        return None
    return (game_id, last_notified)


def sqlite_set_or_update_steam_game(path: Path, game_id: int, date: str):
    """Set an entry from sqlite for Steam or update last_notified if already exists."""
    sqlite_set_notification(path, source="steam", key=str(game_id), last_notified=date)


def sqlite_add_steam_game(path: Path, game_id: int):
    """Add a new entry into sqlite for Steam."""
    date_today = utils.todays_date()
    sqlite_set_notification(
        path, source="steam", key=str(game_id), last_notified=date_today
    )
    print(f"added Steam game {game_id} to DB")


def sqlite_get_epic_entry(path: Path, title: str):
    """Get an entry from sqlite for Epic games notification.

    Returns:
        tuple of (title, date_notified)

    """
    last_notified = sqlite_get_notification(path, source="epic", key=title)
    if last_notified is None:
        return None
    return (title, last_notified)


# TODO: consider saving image or imageUrl
def sqlite_set_epic_entry(path: Path, game: EpicGame, date_notified: str):
    """Set an entry for EpicNotification or update date_notified if already exists."""
    sqlite_set_notification(
        path, source="epic", key=game.title, last_notified=date_notified
    )


def _migrate_legacy_tables(conn: sqlite3.Connection) -> None:
    """Best-effort migration from legacy tables into Notifications."""
    cursor = conn.cursor()

    if _table_exists(conn, "SteamSale"):
        for game_id, last_notified in cursor.execute(
            "SELECT game_id, last_notified FROM SteamSale;"
        ).fetchall():
            cursor.execute(
                "INSERT INTO Notifications (source, entry_key, last_notified) "
                "VALUES (?, ?, ?) "
                "ON CONFLICT(source, entry_key) DO UPDATE SET "
                "last_notified = excluded.last_notified;",
                ("steam", str(game_id), last_notified),
            )

    if _table_exists(conn, "EpicNotification"):
        for title, date_notified in cursor.execute(
            "SELECT title, date_notified FROM EpicNotification;"
        ).fetchall():
            cursor.execute(
                "INSERT INTO Notifications (source, entry_key, last_notified) "
                "VALUES (?, ?, ?) "
                "ON CONFLICT(source, entry_key) DO UPDATE SET "
                "last_notified = excluded.last_notified;",
                ("epic", title, date_notified),
            )


def _drop_legacy_tables(conn: sqlite3.Connection) -> None:
    """Remove legacy tables after migration (best-effort)."""
    cursor = conn.cursor()
    if _table_exists(conn, "SteamSale"):
        cursor.execute("DROP TABLE SteamSale;")
    if _table_exists(conn, "EpicNotification"):
        cursor.execute("DROP TABLE EpicNotification;")


def init_sqlite_db(path: Path):
    """Initialize database.

    :param Path path: A path to users working directory WITHOUT the filename.
    """
    with get_db_connection(path) as conn:
        cursor = conn.cursor()

        notifications_table = """
            CREATE TABLE IF NOT EXISTS Notifications (
                source TEXT NOT NULL,
                entry_key TEXT NOT NULL,
                last_notified TEXT,
                PRIMARY KEY (source, entry_key)
            );
        """
        cursor.execute(notifications_table)

        _migrate_legacy_tables(conn)
        _drop_legacy_tables(conn)
    print("SETUP: database initialized")
