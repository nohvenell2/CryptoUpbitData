from saveprice import save_minute_price
from datetime import datetime
MARKETS = ["KRW-BTC", "KRW-ETH", "KRW-XRP"]

def main(debug=True):
    if debug:
        print(f"================= {datetime.now()} 분봉 데이터 저장 시작")
    for market in MARKETS:
        save_minute_price(market,days=7,candle_type='1hour')
    if debug:
        print(f"================= {datetime.now()} 분봉 데이터 저장 완료")

if __name__ == "__main__":
    main(debug=True)
