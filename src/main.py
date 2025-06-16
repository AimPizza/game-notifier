"""Game Notifier main module.

monitors for changes according to preferences set in .env file and notifies via [ntfy](https://ntfy.sh/)
"""

from datetime import datetime
import os
import sys
import time
from game_notifier import fetcher, notifier, utils, database
from pathlib import Path
import dotenv


def handle_notifications(
    topic: str,
    poll_interval: int,
    notify_epic: bool,
    steam_game_ids: list[int],
    working_dir: Path,
):
    """Execute program logic after everything is set up."""
    while True:
        if notify_epic:
            free_epic_games = fetcher.epic_free_games()
            for game in free_epic_games:
                if utils.epic_should_notify(working_dir, game):
                    database.sqlite_set_epic_entry(
                        working_dir, game, utils.todays_date()
                    )
                    print('sending notification for EpicGames:', game)
                    notifier.send_ntfy(
                        topic, f'{game} is currently free on Epic Games!'
                    )

        if steam_game_ids[0]:
            for id in steam_game_ids:
                message = fetcher.steam_sale(id)
                if message and utils.steam_should_notify(working_dir, id):
                    database.sqlite_set_or_update_steam_game(
                        working_dir, id, utils.todays_date()
                    )
                    print('sending notification for Steam:', id)
                    notifier.send_ntfy(topic, message)

        print('done checking:', datetime.now())
        time.sleep(poll_interval * 60)


def init(working_dir: Path):
    """Initialize everything in order to set everything up.

    :param Path working_dir: working directory where to store file (without filename)
    """
    print('trying to init database..')
    database.init_sqlite_db(working_dir)


def main(env_path: Path):
    """Load environment and get started."""
    dotenv.load_dotenv(dotenv_path=env_path)

    topic = os.getenv('NTFY_TOPIC')
    poll_interval = int(os.getenv('POLL_INTERVAL', '60'))
    notify_epic = os.getenv('EPIC_NOTIFY_FREE_GAMES', '').lower() in (
        'true',
        '1',
        'yes',
    )
    steam_game_ids = [
        int(id.strip()) for id in os.getenv('STEAM_WANTED_GAMES', '').split(',')
    ]

    handle_notifications(
        topic,
        poll_interval,
        notify_epic,
        steam_game_ids,
        utils.remove_env_from_path(env_path),
    )


match sys.argv[1]:
    case 'init':
        path = Path(sys.argv[2])
        init(utils.remove_env_from_path(path))
    case _:
        env_path = Path(sys.argv[1])
        if utils.is_env_path_valid(env_path):
            main(env_path)
