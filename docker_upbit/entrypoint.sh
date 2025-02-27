#!/bin/bash

# 로그 파일 초기화
truncate -s 0 /var/log/cron.log

# 환경변수를 project_env.env에 저장
declare -p | grep -Ev 'BASHOPTS|BASH_VERSINFO|EUID|PPID|SHELLOPTS|UID' > /root/project_env.env
chmod 600 /root/project_env.env  # root만 읽기/쓰기 가능

# cron 시작
service cron start

# 로그 출력
tail -f /var/log/cron.log