import requests

STEAM_API_KEY = "ВАШ_STEAM_API_KEY"

def get_steam_inventory(steam_id):
    url = f"https://steamcommunity.com/inventory/{steam_id}/730/2?l=english&count=5000"
    response = requests.get(url)
    if response.status_code != 200:
        return None

    inventory = response.json()
    items = []
    for asset in inventory.get("assets", []):
        for description in inventory.get("descriptions", []):
            if asset["classid"] == description["classid"]:
                market_hash_name = description["market_hash_name"]
                items.append({
                    "id": asset["assetid"],
                    "name": market_hash_name,
                    "icon": f"https://steamcommunity-a.akamaihd.net/economy/image/{description['icon_url']}",
                })
    return items


def get_skin_price(market_hash_name):
    url = "https://steamcommunity.com/market/priceoverview/"
    params = {
        "currency": "USD",
        "appid": 730,
        "market_hash_name": market_hash_name
    }
    response = requests.get(url).json()
    
    if "lowest_price" not in response:
        return None, None

    steam_price = float(response["lowest_price"].replace("$", ""))
    buy_price = round(steam_price * 0.65, 2)  # 65% от рыночной цены
    return steam_price, buy_price
