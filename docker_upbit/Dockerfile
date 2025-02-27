# Dockerfile
FROM python:3.12.5-slim

# 시간대 설정
ENV TZ=Asia/Seoul
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# poetry 설치
RUN pip install poetry

# 작업 디렉토리 설정
WORKDIR /app

# cron 설치
RUN apt-get update && \
    apt-get install -y --no-install-recommends cron && \
    rm -rf /var/lib/apt/lists/*

# poetry 설정
RUN poetry config virtualenvs.create false

# poetry 의존성 파일 복사
COPY poetry.lock* pyproject.toml ./

# poetry 의존성 설치
RUN poetry install --only main --no-interaction --no-ansi --no-root

# 소스코드 복사
COPY app/upbit ./upbit

# crontab 파일 복사
COPY docker_upbit/crontab /etc/cron.d/crontab

# crontab 파일 권한 설정
RUN chmod 0644 /etc/cron.d/crontab

# crontab 파일 줄바꿈 버그 수정
RUN sed -i 's/\r$//' /etc/cron.d/crontab

# crontab 파일 cron 에 적용
RUN crontab /etc/cron.d/crontab

# entrypoint 스크립트 복사
COPY docker_upbit/entrypoint.sh /entrypoint.sh

# entrypoint 스크립트 권한 설정
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]