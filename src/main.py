import os
import sys
from game_notifier import fetcher, notifier
from pathlib import Path
import dotenv

dotenv.load_dotenv(dotenv_path=Path("/home/rick/tmp/.env"))
topic = os.getenv("NTFY_TOPIC")
steam_game_ids = [id.strip() for id in os.getenv("STEAM_WANTED_GAMES", "").split(",")]
notify_epic = os.getenv("EPIC_NOTIFY_FREE_GAMES", "").lower() in ("true", "1", "yes")


def handle_notifications():
    """the actual program logic to be executed after initialization"""

    if notify_epic:
        free_epic_games = fetcher.epic_free_games()
        for game in free_epic_games:
            notifier.send_ntfy(topic, f"{game} is currently free on Epic Games!")

    if steam_game_ids[0]:
        for id in steam_game_ids:
            msg = fetcher.steam_sale(id)
            if msg:
                notifier.send_ntfy(topic, msg)


# TODO: handle default case
match sys.argv[1]:
    case "init":
        print("initiation go")
    case _:
        print("default case")
        # handle_notifications()
