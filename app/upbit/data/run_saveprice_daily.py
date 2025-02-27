from saveprice import save_daily_price
from datetime import datetime
MARKETS = ["KRW-BTC", "KRW-ETH", "KRW-XRP"]
def main(debug=True):
    if debug:
        print(f"================={datetime.now()} 일봉 데이터 저장 시작")
    for market in MARKETS:
        save_daily_price(market,year=0)
    if debug:
        print(f"================={datetime.now()} 일봉 데이터 저장 완료")

if __name__ == "__main__":
    main(debug=True)
