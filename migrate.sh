#!/bin/bash

# =========================================================
# Alembic 마이그레이션 스크립트 자동 생성 및 적용 쉘 스크립트
#
# 사용법:
#   ./migrate.sh "마이그레이션 메시지"
#
# 예시:
#   ./migrate.sh "Add email column to users table"
#   ./migrate.sh "Create initial tables"
#
# 주의:
#   이 스크립트를 실행하기 전에 DATABASE_URL 환경 변수가 설정되어 있어야 합니다.
#   예: export DATABASE_URL="mysql+mysqlclient://user:password@host:port/dbname"
# =========================================================

# 1. 마이그레이션 메시지 인자 확인
if [ -z "$1" ]; then
  echo "오류: 마이그레이션 메시지를 인자로 제공해야 합니다."
  echo "사용법: ./migrate.sh \"당신의 마이그레이션 메시지\""
  exit 1
fi

MIGRATION_MESSAGE="$1"

# 2. DATABASE_URL 환경 변수 확인
if [ -z "$DATABASE_URL" ]; then
  echo "오류: DATABASE_URL 환경 변수가 설정되지 않았습니다."
  echo "데이터베이스 연결 URL을 설정한 후 다시 시도하십시오."
  echo "예: export DATABASE_URL=\"mysql+mysqlclient://user:password@host:3306/dbname\""
  exit 1
fi

echo "----------------------------------------------------"
echo "Alembic 마이그레이션 시작..."
echo "메시지: \"$MIGRATION_MESSAGE\""
echo "----------------------------------------------------"

# 3. 새로운 마이그레이션 스크립트 생성
echo "새로운 마이그레이션 스크립트 생성 중..."
alembic revision --autogenerate -m "$MIGRATION_MESSAGE"

# 이전 명령의 성공 여부 확인
if [ $? -ne 0 ]; then
  echo "오류: 마이그레이션 스크립트 생성에 실패했습니다."
  exit 1
fi

echo "마이그레이션 스크립트 생성 완료."

# 4. 모든 대기 중인 마이그레이션 적용
echo "모든 대기 중인 마이그레이션 데이터베이스에 적용 중..."
alembic upgrade head

# 이전 명령의 성공 여부 확인
if [ $? -ne 0 ]; then
  echo "오류: 마이그레이션 적용에 실패했습니다."
  exit 1
fi

echo "모든 마이그레이션 성공적으로 적용되었습니다."
echo "----------------------------------------------------"
echo "Alembic 마이그레이션 완료."
echo "----------------------------------------------------"

exit 0