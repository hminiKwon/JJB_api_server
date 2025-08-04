#!/bin/bash

# --- 설정 ---
# 관리할 원본 로그 파일 경로
LOG_FILE="./logs/app.log" 

# 백업 파일을 저장할 디렉토리
BACKUP_DIR="./logs"

# 어제 날짜를 YYYY-MM-DD 형식으로 저장 (자정에 실행되므로 어제 날짜가 맞음)
# --- OS 확인 및 날짜 설정 ---
OS_TYPE=$(uname)
YESTERDAY=""

if [ "$OS_TYPE" == "Darwin" ]; then
  # macOS용 명령어
  echo "macOS 환경을 감지했습니다."
  YESTERDAY=$(date -v-1d +%Y-%m-%d)
elif [ "$OS_TYPE" == "Linux" ]; then
  # 리눅스용 명령어
  echo "리눅스 환경을 감지했습니다."
  YESTERDAY=$(date -d "yesterday" +%Y-%m-%d)
else
  echo "지원하지 않는 운영체제입니다: $OS_TYPE"
  exit 1
fi

# 백업될 로그 파일의 새 이름 설정
BACKUP_FILE="$BACKUP_DIR/$(basename app)-$YESTERDAY.log"

# 원본 로그 파일이 존재하는지 확인
if [ -f "$LOG_FILE" ]; then
    echo "로그 파일 백업을 시작합니다: $LOG_FILE -> $BACKUP_FILE"

    # 1. 로그 파일을 백업 위치로 복사
    cp $LOG_FILE $BACKUP_FILE

    # 2. 원본 로그 파일의 내용을 비움 (서버는 계속 이 파일에 로그를 씀)
    > $LOG_FILE

    # 3. (선택 사항) 백업된 로그 파일을 압축하여 공간 절약
    # gzip $BACKUP_FILE

    echo "로그 백업 완료: $BACKUP_FILE"
else
    echo "로그 파일($LOG_FILE)이 존재하지 않아 작업을 건너뜁니다."
fi

# (선택 사항) 오래된 로그 파일 삭제 (예: 30일보다 오래된 파일)
find $BACKUP_DIR -type f -name "*.gz" -mtime +30 -exec rm {} \;
echo "30일이 지난 오래된 로그를 삭제했습니다."