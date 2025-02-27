from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine, text, String, DateTime, Numeric
import os


# 개발 환경에서는 dotenv 사용
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("개발 환경: .env 파일을 로드했습니다.")
except ImportError:
    print("Docker 환경: 환경변수를 직접 사용합니다.")

# 환경변수 가져오기 (개발환경의 .env 파일 또는 Docker의 환경변수)
try:
    # os.environ.get() 대신 직접 접근
    DB_USER = os.environ['POSTGRES_USER']
    DB_PASSWORD = os.environ['POSTGRES_PASSWORD']
    DB_NAME = os.environ['POSTGRES_DB']
    DB_HOST = os.environ['DB_HOST']
    DB_PORT = os.environ['DB_PORT']

except KeyError as e:
    for key in os.environ:
        if 'POSTGRES' in key or 'DB_' in key:
            print(f"{key}: {os.environ[key]}")
    raise ValueError(f"필수 환경변수가 설정되지 않았습니다: {e}")

from fetch_history import fetch_historical_data_daily, fetch_historical_data_min

def save_daily_price(market,year=3):
    """
    업비트 API 의 일봉 데이터를 DB에 저장하는 함수

    Args:
        market (str): 마켓 코드 (예: 'KRW-BTC')
        year (int): 가져올 연도 수 (기본값: 3), year=0 일때 최근 1주일 데이터 저장함
    """
    try:
        # 데이터 가져오기
        df = fetch_historical_data_daily(market, year)
        if df is None:
            return False
            
        # created_at 컬럼 추가
        df['created_at'] = datetime.now()
        
        # 데이터 타입 변환
        numeric_columns = ['open', 'high', 'low', 'close', 'volume', 'trade_price', 'change_rate']
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # DB 연결
        DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        engine = create_engine(DATABASE_URL)
        
        # 임시 테이블에 데이터 저장
        temp_table = f"temp_{market.replace('-', '_').lower()}"
        df.to_sql(temp_table, engine, if_exists='replace', index=False,
                 dtype={
                     'market': String(20),
                     'timestamp_utc': DateTime(timezone=True),
                     'timestamp_kst': DateTime(timezone=True),
                     'open': Numeric(20, 8),
                     'high': Numeric(20, 8),
                     'low': Numeric(20, 8),
                     'close': Numeric(20, 8),
                     'volume': Numeric(20, 8),
                     'trade_price': Numeric(30, 8),
                     'change_rate': Numeric(10, 4),
                     'created_at': DateTime(timezone=True)
                 })
        
        # INSERT IGNORE 패턴으로 데이터 저장
        with engine.connect() as conn:
            insert_query = text(f"""
                INSERT INTO upbit_daily_price (
                    market, timestamp_utc, timestamp_kst, open, high, low, close,
                    volume, trade_price, change_rate, created_at
                )
                SELECT 
                    market, timestamp_utc, timestamp_kst, open, high, low, close,
                    volume, trade_price, change_rate, created_at
                FROM {temp_table}
                ON CONFLICT (market, timestamp_utc)
                DO NOTHING;
                
                DROP TABLE {temp_table};
            """)
            
            result = conn.execute(insert_query)
            conn.commit()
        
        return True
        
    except Exception as e:
        print(f"데이터 저장 중 오류 발생: {e}")
        return False
    
def save_minute_price(market,days=1,candle_type='1hour'):
    """
    업비트 API 의 분봉 데이터를 DB에 저장하는 함수

    Args:
        market (str): 마켓 코드 (예: 'KRW-BTC')
        days (int): 가져올 일 수 (기본값: 1)
        candle_type (str): 분봉 타입 ('1min', '3min', '5min', '10min', '30min', '1hour')
    """
    if candle_type == '1hour':
        TABLE_NAME = 'upbit_1hour_price'
    elif candle_type in ['1min', '3min', '5min', '10min', '30min']:
        TABLE_NAME = 'upbit_minute_price'
    else:
        raise ValueError(f"지원하지 않는 캔들 유형: {candle_type}")
    
    try:
        # 데이터 가져오기
        df = fetch_historical_data_min(market, days, candle_type=candle_type)
        if df is None:
            return False
            
        # created_at 컬럼 추가
        df['created_at'] = datetime.now()
        
        # 데이터 타입 변환
        numeric_columns = ['open', 'high', 'low', 'close', 'volume', 'trade_price']
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # DB 연결
        DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        engine = create_engine(DATABASE_URL)
        
        # 임시 테이블에 데이터 저장
        temp_table = f"temp_{market.replace('-', '_').lower()}"
        df.to_sql(temp_table, engine, if_exists='replace', index=False,
                 dtype={
                     'market': String(20),
                     'timestamp_utc': DateTime(timezone=True),
                     'timestamp_kst': DateTime(timezone=True),
                     'open': Numeric(20, 8),
                     'high': Numeric(20, 8),
                     'low': Numeric(20, 8),
                     'close': Numeric(20, 8),
                     'volume': Numeric(20, 8),
                     'trade_price': Numeric(30, 8),
                     'created_at': DateTime(timezone=True)
                 })
        
        # INSERT IGNORE 패턴으로 데이터 저장
        with engine.connect() as conn:
            insert_query = text(f"""
                INSERT INTO {TABLE_NAME} (
                    market, timestamp_utc, timestamp_kst, open, high, low, close,
                    volume, trade_price, created_at
                )
                SELECT 
                    market, timestamp_utc, timestamp_kst, open, high, low, close,
                    volume, trade_price, created_at
                FROM {temp_table}
                ON CONFLICT (market, timestamp_utc)
                DO NOTHING;
                
                DROP TABLE {temp_table};
            """)
            
            result = conn.execute(insert_query)
            conn.commit()
        
        return True
        
    except Exception as e:
        print(f"데이터 저장 중 오류 발생: {e}")
        return False

if __name__ == "__main__":
    # 테스트: 비트코인 200일 데이터 저장
    success = save_minute_price("KRW-BTC",days=1)
    if success:
        print("저장 성공!")
    else:
        print("저장 실패!")