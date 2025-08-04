# JJB_api_server

## 테스트 방법

1. ssh -L 3306:127.0.0.1:3306 {user}@{ssh_server} (서버 실행시 제외)
2. sh ./run.sh

## DB 수정시 마이그레이션 진행 필요

1. ssh -L 3306:127.0.0.1:3306 {user}@{ssh_server} (서버 실행시 제외)
2. sh ./migrate.sh

## ENV

### .env 작성 필요

- JANUS_SERVER_URL
- DATABASE_URL
