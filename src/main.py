"""Game Notifier main module.

monitors for changes according to preferences set in .env file and notifies via [ntfy](https://ntfy.sh/)
"""

import argparse
import os
import sys
from game_notifier import notifier, database, install
from pathlib import Path
import dotenv


def init(config_dir: Path, script_dir: Path, skip_service: bool):
    """Initialize everything in order to set everything up.

    :param Path working_dir: working directory where to store file (without filename)
    """
    print("trying to init database..")
    database.init_sqlite_db(config_dir)

    if not skip_service:
        print(
            f"Installing service with config directory: {config_dir} "
            f"and script directory: {script_dir}"
        )
        install.setup_game_notifier_instance(config_dir, script_dir)


def parse_args():
    """Handle provided arguments."""
    parser = argparse.ArgumentParser(description="Install or run the game-notifier")

    main_group = parser.add_mutually_exclusive_group(required=True)
    main_group.add_argument(
        "-i", "--install", action="store_true", help="Install service"
    )
    main_group.add_argument("-r", "--run", action="store_true", help="Run the notifier")

    parser.add_argument(
        "-c",
        "--config-dir",
        type=Path,
        default=Path(__file__).parent.parent,
        help="Path to directory containing your .env",
    )
    parser.add_argument(
        "-s", "--script-dir", type=Path, default=Path(__file__), help="Path to main.py"
    )
    parser.add_argument(
        "--no-service",
        action="store_true",
        help="Skip installation of the systemd service. Useful on non-standard distros",
    )

    args = parser.parse_args(sys.argv[1:] or ["--run"])

    if not args.script_dir.exists():
        print(f"Error: script not found at {args.script_dir}", file=sys.stderr)
        sys.exit(1)
    if not args.config_dir.is_dir():
        print(
            f"Error: config_dir is not a directory: {args.config_dir}", file=sys.stderr
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
        dotenv_path = config_dir / ".env"
        dotenv.load_dotenv(dotenv_path)

        topic = os.getenv("NTFY_TOPIC")
        if not topic:
            print("Error: no topic set (NTFY_TOPIC)")
            sys.exit(1)
        poll_interval = int(os.getenv("POLL_INTERVAL", "60"))
        notify_epic = os.getenv("EPIC_NOTIFY_FREE_GAMES", "").lower() in (
            "true",
            "1",
            "yes",
        )
        steam_game_ids: list[int] = []
        for raw_id in os.getenv("STEAM_WANTED_GAMES", "").split(","):
            raw_id = raw_id.strip()
            if not raw_id:
                continue
            try:
                steam_game_ids.append(int(raw_id))
            except ValueError:
                continue

        notifier.loop(topic, poll_interval, notify_epic, steam_game_ids, config_dir)


if __name__ == "__main__":
    main()
