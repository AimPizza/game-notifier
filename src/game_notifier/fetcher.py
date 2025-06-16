"""Interacts with external APIs to retrieve data about games."""

from datetime import datetime, timezone
import requests

# TODO: allow for configuration
# hard-coded values for games available in Germany
LOCALE = 'de'
LANGUAGE = 'german'
COUNTRY = 'DE'
ALLOW_COUNTRIES = 'DE'


def epic_is_currently_free(game: dict) -> bool:
    """Inspect a single game and determines whether it is free right now."""
    # most games that are no longer free have this field set to `None`
    promo = game.get('promotions', {})
    if not promo:
        return False

    offers = promo.get('promotionalOffers') or []
    for block in offers:
        for offer in block.get('promotionalOffers', []):
            # Prüfe, ob discountPrice == 0 und Datum aktuell
            if offer.get('discountSetting', {}).get('discountType') == 'PERCENTAGE':
                start = datetime.fromisoformat(
                    offer['startDate'].replace('Z', '+00:00')
                )
                end = datetime.fromisoformat(offer['endDate'].replace('Z', '+00:00'))
                now = datetime.now(timezone.utc)
                price = game.get('price', {}).get('totalPrice', {}).get('discountPrice')
                if price == 0 and start <= now <= end:
                    return True
    return False


def epic_free_games() -> list[str]:
    """Return a list of the games that are currently free on epicgames."""
    free_games = []

    with requests.get(
        'https://store-site-backend-static-ipv4.ak.epicgames.com/freeGamesPromotions?'
        f'locale={LOCALE}&country={COUNTRY}&allowCountries={ALLOW_COUNTRIES}'
    ) as response:
        games = response.json()['data']['Catalog']['searchStore']['elements']
        for game in games:
            if epic_is_currently_free(game):
                free_games.append(game['title'])

    return free_games


# https://github.com/Revadike/InternalSteamWebAPI/wiki/Get-App-Details
# TODO: handle if f2p game is provided - price_overview will be missing then
def steam_sale(appid: int) -> str:
    """Return a message composed for a given steam game's appid in case it is on sale.

    :param int appid: valid Steam appid
    """
    message = ''

    with requests.get(
        'https://store.steampowered.com/api/appdetails?'
        f'appids={appid}&cc={LOCALE}&l={LANGUAGE}'
    ) as response:
        game_info = response.json()[str(appid)]['data']
        game_price_info = game_info['price_overview']

        if game_price_info['discount_percent'] > 0:
            game_name = game_info['name']
            message = (
                f'{game_name} is on sale for {game_price_info["final_formatted"]}!'
                f' (-{game_price_info["discount_percent"]}%)'
            )

    return message
