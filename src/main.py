"""Game Notifier main module.

monitors for changes according to preferences set in .env file and notifies via [ntfy](https://ntfy.sh/)
"""

import argparse
from datetime import datetime
import os
import sys
import time
from game_notifier import fetcher, notifier, utils, database, install
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

        print(
            f'done, next iteration in {poll_interval}min, time now is:',
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        )
        time.sleep(poll_interval * 60)


def init(config_dir: Path, script_dir: Path, skip_service: bool):
    """Initialize everything in order to set everything up.

    :param Path working_dir: working directory where to store file (without filename)
    """
    print('trying to init database..')
    database.init_sqlite_db(config_dir)

    if not skip_service:
        print(
            f'Installing service with config directory: {config_dir} '
            f'and script directory: {script_dir}'
        )
        install.setup_game_notifier_instance(config_dir, script_dir)


def parse_args():
    """Handle provided arguments."""
    parser = argparse.ArgumentParser(description='Install or run the game-notifier')

    main_group = parser.add_mutually_exclusive_group(required=True)
    main_group.add_argument(
        '-i', '--install', action='store_true', help='Install service'
    )
    main_group.add_argument('-r', '--run', action='store_true', help='Run the notifier')

    parser.add_argument(
        '-c',
        '--config-dir',
        type=Path,
        default=Path(__file__).parent.parent,
        help='Path to directory containing your .env',
    )
    parser.add_argument(
        '-s', '--script-dir', type=Path, default=Path(__file__), help='Path to main.py'
    )
    parser.add_argument(
        '--no-service',
        type=bool,
        default=False,
        help='Skip installation of the systemd service. Useful on non-standard distros',
    )

    args = parser.parse_args(sys.argv[1:] or ['--run'])

    if not args.script_dir.exists():
        print(f'Error: script not found at {args.script_dir}', file=sys.stderr)
        sys.exit(1)
    if not args.config_dir.is_dir():
        print(
            f'Error: config_dir is not a directory: {args.config_dir}', file=sys.stderr
        )
        sys.exit(1)
    return args


def main():
    """Load environment and get started."""
    args = parse_args()

    config_dir = args.config_dir.resolve()
    script_dir = args.script_dir.resolve()
    skip_service_installation = args.no_service

    if args.install:
        init(config_dir, script_dir, skip_service_installation)
    elif args.run:
        dotenv_path = config_dir / '.env'
        print(f'DEBUG dotenv_path: {dotenv_path}')
        dotenv.load_dotenv(dotenv_path)

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
            topic, poll_interval, notify_epic, steam_game_ids, config_dir
        )


if __name__ == '__main__':
    main()
