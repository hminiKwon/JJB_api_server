import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Janus 서버의 REST API 주소
    JANUS_SERVER_URL: str = "http://127.0.0.1:8088/janus"

    class Config:
        # .env 파일을 읽어오도록 설정
        env_file = ".env"

# 설정 객체 생성
settings = Settings()