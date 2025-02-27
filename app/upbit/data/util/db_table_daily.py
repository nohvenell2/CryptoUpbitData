from sqlalchemy import create_engine, Column, String, DateTime, Numeric, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import UniqueConstraint
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 환경변수 가져오기
DB_USER = os.getenv('POSTGRES_USER')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD')
DB_NAME = os.getenv('POSTGRES_DB')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')

# Base 클래스 생성
Base = declarative_base()
# 일봉 테이블
class UpbitDailyPrice(Base):
    __tablename__ = 'upbit_daily_price'
    
    id = Column(Integer, primary_key=True)
    market = Column(String(20), nullable=False)
    timestamp_utc = Column(DateTime(timezone=True), nullable=False)
    timestamp_kst = Column(DateTime(timezone=True), nullable=False)
    open = Column(Numeric(20, 8), nullable=False)
    high = Column(Numeric(20, 8), nullable=False)
    low = Column(Numeric(20, 8), nullable=False)
    close = Column(Numeric(20, 8), nullable=False)
    volume = Column(Numeric(20, 8), nullable=False)
    trade_price = Column(Numeric(30, 8), nullable=False)
    change_rate = Column(Numeric(10, 4), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    
    # market과 timestamp의 조합을 unique로 설정
    __table_args__ = (
        UniqueConstraint('market', 'timestamp_utc', name='uix_market_daily_timestamp_utc'),
    )

def create_tables():
    try:
        # 데이터베이스 연결 설정
        DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        engine = create_engine(DATABASE_URL)
        
        # 테이블 생성
        Base.metadata.create_all(engine)
        print("테이블이 성공적으로 생성되었습니다.")
        
    except Exception as e:
        print(f"테이블 생성 중 오류 발생: {e}")

if __name__ == "__main__":
    create_tables()
