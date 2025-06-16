import os
import sys
from game_notifier import fetcher, notifier
from pathlib import Path
import dotenv

def handle_notifications(topic, notify_epic, steam_game_ids):
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

def init():
    print("init the program... (logic to be defined)")

def main(env_path: Path):
    dotenv.load_dotenv(dotenv_path=Path("/home/rick/tmp/.env"))
    topic = os.getenv("NTFY_TOPIC")
    steam_game_ids = [id.strip() for id in os.getenv("STEAM_WANTED_GAMES", "").split(",")]
    notify_epic = os.getenv("EPIC_NOTIFY_FREE_GAMES", "").lower() in ("true", "1", "yes")

    handle_notifications(topic, notify_epic, steam_game_ids)

match sys.argv[1]:
    case "init":
        init()
    case _:
        main(sys.argv[1]) # assuming that's the path
