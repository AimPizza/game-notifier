import os
from game_notifier import fetcher, notifier
import dotenv

dotenv.load_dotenv()
topic = os.getenv("NTFY_TOPIC")
steam_game_ids = [id.strip() for id in os.getenv("STEAM_WANTED_GAMES").split(",")]

free_epic_games = fetcher.epic_free_games()
for game in free_epic_games:
    notifier.send_ntfy(topic, f"{game} is currently free on Epic Games!")

for id in steam_game_ids:
    msg = fetcher.steam_sale(id)
    if msg:
        notifier.send_ntfy(topic, msg)
