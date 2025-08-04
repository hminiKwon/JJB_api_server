#!/bin/bash

# --- 설정 ---
PORT=9991
VENV_PYTHON="./venv/bin/python"
VENV_UVICORN="./venv/bin/uvicorn"

# --- 1. 기존 서버 종료 ---
echo "포트 $PORT 에서 실행 중인 서버를 확인합니다..."
PID=$(lsof -t -i:$PORT)

if [ -n "$PID" ]; then
  echo "기존 서버(PID: $PID)를 종료합니다."
  kill $PID
  # 프로세스가 완전히 종료될 때까지 잠시 대기
  sleep 2
else
  echo "실행 중인 서버가 없습니다."
fi

# --- 2. 의존성 설치 ---
echo "requirements.txt 의존성을 설치합니다..."
# 가상 환경의 python을 이용해 pip를 실행하여 설치
$VENV_PYTHON -m pip install -r requirements.txt

# 설치 성공 여부 확인
if [ $? -ne 0 ]; then
    echo "의존성 설치에 실패했습니다. 스크립트를 중단합니다."
    exit 1
fi

echo "의존성 설치 완료."

# echo "DataBase Migration을 진행합니다."
# sh ./migrate.sh

# --- 3. 새 서버 실행 ---
echo "새로운 서버를 포트 $PORT 에서 시작합니다."
# 가상 환경의 uvicorn을 직접 실행
$VENV_UVICORN app.main:app --reload --port $PORT >> ./logs/app.log 2>&1 &

echo "서버가 백그라운드에서 실행되었습니다."