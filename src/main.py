import os
from game_notifier import fetcher, notifier
import dotenv

dotenv.load_dotenv()
topic = os.getenv("NTFY_TOPIC")

free_epic_games = fetcher.epic_free_games()
if free_epic_games:
    for game in free_epic_games:
        notifier.send_ntfy(topic, f"{game} is currently free on Epic Games!")
