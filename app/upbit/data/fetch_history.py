from datetime import datetime, timedelta
import pandas as pd
import time
from fetch_candle import fetch_candle_day, fetch_candle_min

DELAY = 0.3
def fetch_historical_data_daily(market, years=3):
    """
    지정된 기간(년)만큼의 과거 일봉 데이터를 가져오는 함수
    
    Args:
        market (str): 마켓 코드 (예: 'KRW-BTC')
        years (int): 가져올 연도 수 (기본값: 3), year=0 일때 최근 1주일 데이터 가져옴
    
    Returns:
        DataFrame or None: 성공시 DataFrame, 실패시 None
    """
    try:
        all_data = []
        current_time = datetime.now()
        
        # 3년치 데이터는 약 1095일 (365 * 3)
        total_days = years * 365
        if years == 0:
            total_days = 7
        remaining_days = total_days
        print(f"{market} {years}년치 데이터 수집 시작...")
        
        while remaining_days > 0:
            # 현재 배치에서 가져올 데이터 수 결정
            batch_size = min(200, remaining_days)
            
            # 데이터 가져오기
            df_batch = fetch_candle_day(
                market=market,
                count=batch_size,
                time=current_time.strftime('%Y-%m-%d %H:%M:%S')
            )
            
            if df_batch is None or df_batch.empty:
                print(f"데이터 가져오기 실패: {current_time}")
                break
                
            # 데이터 저장
            all_data.append(df_batch)
            
            # 다음 배치를 위한 마지막 timestamp 설정
            current_time = df_batch['timestamp_utc'].min() - timedelta(days=1)
            remaining_days -= batch_size
            """
            # 진행상황 출력
            progress = ((total_days - remaining_days) / total_days) * 100
            print(f"진행률: {progress:.1f}% ({total_days - remaining_days}/{total_days}일)")
            """            
            # API 호출 간격 조절
            time.sleep(DELAY)
        
        if not all_data:
            return None
            
        # 모든 데이터 합치기
        final_df = pd.concat(all_data, ignore_index=True)
        
        # 중복 제거 및 정렬
        final_df = final_df.drop_duplicates(subset=['market', 'timestamp_utc'])
        final_df = final_df.sort_values('timestamp_utc')
        
        print(f"{market} {years}년치 데이터 수집 완료: 총 {len(final_df)}개 데이터")
        print(f"기간: {final_df['timestamp_utc'].min()} ~ {final_df['timestamp_utc'].max()}")
        
        return final_df
        
    except Exception as e:
        print(f"데이터 수집 중 오류 발생: {e}")
        return None

def fetch_historical_data_min(market, days=365, candle_type='5min'):
    """
    지정된 기간(일)만큼의 과거 분봉 데이터를 가져오는 함수
    
    Args:
        market (str): 마켓 코드 (예: 'KRW-BTC')
        days (int): 가져올 일 수 (기본값: 365)
        candle_type (str): 분봉 타입 ('1min', '3min', '5min', '10min', '30min', '1hour')
    
    Returns:
        DataFrame or None: 성공시 DataFrame, 실패시 None
    """
    try:
        all_data = []
        current_time = datetime.now()
        
        # 하루에 필요한 API 호출 횟수 계산
        if candle_type == '1min':
            candles_per_day = 1440  # 24시간 * 60분
        elif candle_type == '3min':
            candles_per_day = 480   # 24시간 * 20
        elif candle_type == '5min':
            candles_per_day = 288   # 24시간 * 12
        elif candle_type == '10min':
            candles_per_day = 144   # 24시간 * 6
        elif candle_type == '30min':
            candles_per_day = 48    # 24시간 * 2
        elif candle_type == '1hour':
            candles_per_day = 24    # 24시간
        
        total_candles = days * candles_per_day
        remaining_candles = total_candles
        
        print(f"{market} {days}일치 {candle_type} 데이터 수집 시작...")
        
        while remaining_candles > 0:
            # 현재 배치에서 가져올 데이터 수 결정
            batch_size = min(200, remaining_candles)
            
            # 데이터 가져오기
            df_batch = fetch_candle_min(
                market=market,
                count=batch_size,
                time=current_time.strftime('%Y-%m-%d %H:%M:%S'),
                candle_type=candle_type
            )
            
            if df_batch is None or df_batch.empty:
                print(f"데이터 가져오기 실패: {current_time}")
                break
                
            # 데이터 저장
            all_data.append(df_batch)
            
            # 다음 배치를 위한 마지막 timestamp 설정
            current_time = df_batch['timestamp_utc'].min()
            remaining_candles -= batch_size
            """            
            # 진행상황 출력
            progress = ((total_candles - remaining_candles) / total_candles) * 100
            print(f"진행률: {progress:.1f}% ({total_candles - remaining_candles}/{total_candles}개)")
            """            
            # API 호출 간격 조절
            time.sleep(DELAY)
        
        if not all_data:
            return None
            
        # 모든 데이터 합치기
        final_df = pd.concat(all_data, ignore_index=True)
        
        # 중복 제거 및 정렬
        final_df = final_df.drop_duplicates(subset=['market', 'timestamp_utc'])
        final_df = final_df.sort_values('timestamp_utc')
        
        print(f"{market} {days}일치 {candle_type} 데이터 수집 완료: 총 {len(final_df)}개 데이터")
        print(f"기간: {final_df['timestamp_utc'].min()} ~ {final_df['timestamp_utc'].max()}")
        
        return final_df
        
    except Exception as e:
        print(f"데이터 수집 중 오류 발생: {e}")
        return None

if __name__ == "__main__":
    # 테스트: 비트코인 데이터 가져오기
    markets = ["KRW-BTC"]
    
    for market in markets:
        # 일봉 데이터
        df_day = fetch_historical_data_daily(market, years=0)
        if df_day is not None:
            print(f"\n=== {market} 일봉 데이터 미리보기 ===")
            print(df_day.head())
        """
        # 분봉 데이터
        df_min = fetch_historical_data_min(market, days=1, candle_type='5min')
        if df_min is not None:
            print(f"\n=== {market} 5분봉 데이터 미리보기 ===")
            print(df_min.head())
        """
