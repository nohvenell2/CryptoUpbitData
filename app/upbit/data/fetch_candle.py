import requests
from datetime import datetime, timezone
import pytz
import pandas as pd

def fetch_candle_day(market, count=200, time=None):
    """
    업비트에서 일간 캔들 데이터를 가져오는 함수
    
    Args:
        market (str): 마켓 코드 (예: 'KRW-BTC')
        count (int): 가져올 캔들 개수 (최대 200)
        time (str): 기준 시점 (예: '2024-01-22 00:00:00')
        candle_type (str): 캔들 타입 ('min' 또는 'day')
    
    Returns:
        DataFrame or None: 성공시 DataFrame, 실패시 None
    """
    try:
        # count 값 검증
        if count > 200:
            count = 200
            print("최대 200개까지만 가져올 수 있습니다. count를 200으로 설정합니다.")
        
        url = "https://api.upbit.com/v1/candles/days"
        
        # 파라미터 설정
        params = {
            "market": market,
            "count": count,
        }
        if time is not None:
            params['to'] = time
        
        # API 요청
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # 데이터 정제
        df = pd.DataFrame(data)
        df = df[[
            'market',
            'candle_date_time_utc',
            'candle_date_time_kst',
            'opening_price',
            'high_price',
            'low_price',
            'trade_price',
            'candle_acc_trade_volume',
            'candle_acc_trade_price',
            'change_rate'
        ]]
        
        # 컬럼명 변경
        df.columns = [
            'market',
            'timestamp_utc',
            'timestamp_kst',
            'open',
            'high',
            'low',
            'close',
            'volume',
            'trade_price',
            'change_rate'
        ]
        
        # timestamp를 datetime으로 변환
        df['timestamp_utc'] = pd.to_datetime(df['timestamp_utc'])
        df['timestamp_kst'] = pd.to_datetime(df['timestamp_kst'])
        
        # 시간순 정렬 (과거 -> 현재)
        df = df.sort_values('timestamp_utc')
        
        return df
        
    except requests.exceptions.RequestException as e:
        print(f"API 요청 실패: {e}")
        return None
    except Exception as e:
        print(f"에러 발생: {e}")
        return None
    
def fetch_candle_min(market, count=200, time=None, candle_type='5min'):
    """
    업비트에서 분봉 캔들 데이터를 가져오는 함수
    
    Args:
        market (str): 마켓 코드 (예: 'KRW-BTC')
        count (int): 가져올 캔들 개수 (최대 200)
        time (str): 기준 시점 (예: '2024-01-22 00:00:00')
        candle_type (str): 캔들 타입 ('1min', '3min', '5min', '10min', '30min', '1hour')
    
    Returns:
        DataFrame or None: 성공시 DataFrame, 실패시 None
    """
    try:
        # count 값 검증
        if count > 200:
            count = 200
            print("최대 200개까지만 가져올 수 있습니다. count를 200으로 설정합니다.")
        if candle_type == '1min':
            url = "https://api.upbit.com/v1/candles/minutes/1"
        elif candle_type == '3min':
            url = "https://api.upbit.com/v1/candles/minutes/3"
        elif candle_type == '5min':
            url = "https://api.upbit.com/v1/candles/minutes/5"
        elif candle_type == '10min':
            url = "https://api.upbit.com/v1/candles/minutes/10"
        elif candle_type == '30min':
            url = "https://api.upbit.com/v1/candles/minutes/30"
        elif candle_type == '1hour':
            url = "https://api.upbit.com/v1/candles/minutes/60"
        
        # 파라미터 설정
        params = {
            "market": market,
            "count": count,
        }
        if time is not None:
            params['to'] = time
        
        # API 요청
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # 데이터 정제
        df = pd.DataFrame(data)
        df = df[[
            'market',
            'candle_date_time_utc',
            'candle_date_time_kst',
            'opening_price',
            'high_price',
            'low_price',
            'trade_price',
            'candle_acc_trade_volume',
            'candle_acc_trade_price',
        ]]
        
        # 컬럼명 변경
        df.columns = [
            'market',
            'timestamp_utc',
            'timestamp_kst',
            'open',
            'high',
            'low',
            'close',
            'volume',
            'trade_price',
        ]
        # timestamp를 datetime으로 변환
        df['timestamp_utc'] = pd.to_datetime(df['timestamp_utc'])
        df['timestamp_kst'] = pd.to_datetime(df['timestamp_kst'])
        
        # 시간순 정렬 (과거 -> 현재)
        df = df.sort_values('timestamp_utc')
        
        return df
        
    except requests.exceptions.RequestException as e:
        print(f"API 요청 실패: {e}")
        return None
    except Exception as e:
        print(f"에러 발생: {e}")
        return None
    
if __name__ == "__main__":
    # 테스트: 비트코인 데이터 가져오기
    # 일봉 테스트
    df_day = fetch_candle_day("KRW-BTC", 5, '2024-01-22 00:00:00')
    if df_day is not None:
        print("\n=== 일봉 데이터 미리보기 ===")
        print(df_day.head())
    
    # 분봉 테스트
    df_min = fetch_candle_min("KRW-BTC", 5, '2024-01-22 00:00:00', '1hour')
    if df_min is not None:
        print("\n=== 분봉 데이터 미리보기 ===")
        print(df_min.head())    