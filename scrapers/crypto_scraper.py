from pycoingecko import CoinGeckoAPI

def fetch_crypto_trending():
    """Fetch trending cryptocurrencies from CoinGecko."""
    cg = CoinGeckoAPI()
    trending = cg.get_search_trending()
    results = []
    for coin in trending["coins"]:
        item = coin["item"]
        results.append({
            "name": item["name"],
            "symbol": item["symbol"],
            "market_cap_rank": item.get("market_cap_rank"),
            "price_btc": item["price_btc"],
            "url": f"https://www.coingecko.com/en/coins/{item['id']}"
        })
    return results
