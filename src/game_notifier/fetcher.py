"""
Interacts with external APIs to retrieve data about games
"""

from datetime import datetime, timezone
import requests


def is_currently_free(game: dict) -> bool:
    """inspects a single game and determines whether it is free right now"""

    # most games that are no longer free have this field set to `None`
    promo = game.get("promotions", {})
    if not promo:
        return False

    offers = promo.get("promotionalOffers") or []
    for block in offers:
        for offer in block.get("promotionalOffers", []):
            # Prüfe, ob discountPrice == 0 und Datum aktuell
            if offer.get("discountSetting", {}).get("discountType") == "PERCENTAGE":
                start = datetime.fromisoformat(
                    offer["startDate"].replace("Z", "+00:00")
                )
                end = datetime.fromisoformat(offer["endDate"].replace("Z", "+00:00"))
                now = datetime.now(timezone.utc)
                price = game.get("price", {}).get("totalPrice", {}).get("discountPrice")
                if price == 0 and start <= now <= end:
                    return True
    return False


def epic_free_games() -> list[str]:
    """returns a list of the games that are currently free on epicgames"""

    free_games = []

    # TODO: allow for configuration
    # hard-coded values for games available in Germany
    locale = "de"
    country = "DE"
    allow_countries = "DE"

    with requests.get(
        "https://store-site-backend-static-ipv4.ak.epicgames.com/freeGamesPromotions?"
        f"locale={locale}&country={country}&allowCountries={allow_countries}"
    ) as response:
        games = response.json()["data"]["Catalog"]["searchStore"]["elements"]
        for game in games:
            if is_currently_free(game):
                free_games.append(game["title"])

    return free_games
