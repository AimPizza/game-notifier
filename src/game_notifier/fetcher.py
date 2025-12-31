"""Interacts with external APIs to retrieve data about games."""

from datetime import datetime, timezone
from typing import Optional
import requests

from game_notifier.models import EpicGame, SteamSaleHit

# TODO: allow for configuration
# hard-coded values for games available in Germany
LOCALE = "de"
LANGUAGE = "german"
COUNTRY = "DE"
ALLOW_COUNTRIES = "DE"

EpicResponseGame = dict


def epic_is_currently_free(game: EpicResponseGame) -> bool:
    """Inspect a single game and determines whether it is free right now."""
    # most games that are no longer free have this field set to `None`
    promo = game.get("promotions", {})
    if not promo:
        return False

    offers = promo.get("promotionalOffers") or []
    for block in offers:
        for offer in block.get("promotionalOffers", []):
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


def epic_get_banner_url(game: EpicResponseGame) -> str:
    wanted_image_types = ["OfferImageWide"]
    for image_obj in game["keyImages"]:
        if image_obj["type"] in wanted_image_types:
            return image_obj["url"]

    return ""


def epic_build_store_url(slug: str) -> str:
    return f"https://epicgames.com/{LOCALE}/p/{slug}"


def epic_free_games() -> list[EpicGame]:
    """Return a list of the games that are currently free on epicgames."""
    free_games: list[EpicGame] = []

    with requests.get(
        "https://store-site-backend-static-ipv4.ak.epicgames.com/freeGamesPromotions?"
        f"locale={LOCALE}&country={COUNTRY}&allowCountries={ALLOW_COUNTRIES}"
    ) as response:
        games: list[EpicResponseGame] = response.json()["data"]["Catalog"][
            "searchStore"
        ]["elements"]
        for game in games:
            if epic_is_currently_free(game):
                banner = epic_get_banner_url(game)
                store = epic_build_store_url(game["productSlug"])
                free_games.append(
                    EpicGame(title=game["title"], banner_url=banner, store_url=store)
                )

    return free_games


# https://github.com/Revadike/InternalSteamWebAPI/wiki/Get-App-Details
# TODO: handle if f2p game is provided - price_overview will be missing then
def steam_sale(appid: int) -> Optional[SteamSaleHit]:
    """Return a message composed for a given steam game's appid in case it is on sale.

    :param int appid: valid Steam appid
    """
    message = ""

    with requests.get(
        "https://store.steampowered.com/api/appdetails?"
        f"appids={appid}&cc={LOCALE}&l={LANGUAGE}"
    ) as response:
        game_info = response.json()[str(appid)]["data"]
        game_price_info = game_info["price_overview"]

        if game_price_info["discount_percent"] > 0:
            steam_game = SteamSaleHit(
                title=game_info["name"],
                appid=appid,
                discount_percentage=game_price_info["discount_percent"],
                banner_url=game_info["header_image"],
                price=game_price_info["final_formatted"],
            )

            return steam_game
