# app/core/config.py (개선된 버전)
import os
from pydantic_settings import BaseSettings, SettingsConfigDict # pydantic_settings에서 import
from dotenv import load_dotenv

load_dotenv() # .env 파일 로드

class Settings(BaseSettings):
    JANUS_SERVER_URL: str
    DATABASE_URL: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    # extra="ignore"는 .env 파일에 model_config에 정의되지 않은 변수가 있어도 무시하고 경고를 띄우지 않습니다.

# 설정 객체 생성
settings = Settings()