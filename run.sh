#!/bin/bash

# 확인할 포트 번호
PORT=9991

echo "포트 $PORT 확인 중..."

# lsof 명령어로 해당 포트를 사용하는 프로세스의 PID를 찾습니다.
# -t 옵션은 PID 번호만 깔끔하게 출력합니다.
PID=$(lsof -t -i:$PORT)

# PID 변수에 값이 있는지 (프로세스가 존재하는지) 확인합니다.
if [ -n "$PID" ]; then
  echo "포트 $PORT 에서 실행 중인 프로세스(PID: $PID)를 발견했습니다."
  echo "프로세스를 종료합니다..."
  kill $PID
  echo "완료!"
else
  echo "포트 $PORT 에서 실행 중인 프로세스가 없습니다."
fi

echo "백엔드 파이썬 서버를 실행합니다."

nohup ./venv/bin/uvicorn app.main:app --port 9991 &