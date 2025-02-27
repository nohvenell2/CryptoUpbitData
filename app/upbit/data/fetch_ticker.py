import requests 

def fetch_ticker(markets):
    url = f"https://api.upbit.com/v1/ticker"
    marketsString = ",".join(markets)
    params = {
        "markets": marketsString
    }
    headers = {
        "accept": "application/json"
    }
    res = requests.get(url, params=params, headers=headers)
    return res.json()

if __name__ == "__main__":
    markets = ["KRW-BTC", "KRW-ETH", "KRW-XRP"]
    print(fetch_ticker(markets))
