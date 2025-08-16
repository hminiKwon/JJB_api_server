# app/core/config.py (개선된 버전)
from functools import lru_cache
import os
from pydantic_settings import BaseSettings, SettingsConfigDict # pydantic_settings에서 import
from dotenv import load_dotenv

load_dotenv() # .env 파일 로드

class Settings(BaseSettings):
    JANUS_SERVER_URL: str
    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALG: str
    ACCESS_EXPIRE_MINUTES: int
    REFRESH_EXPIRE_DAYS: int
    REFRESH_HASH_PEPPER: str
    COOKIE_SAMESITE: str
    COOKIE_SECURE: bool

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    # extra="ignore"는 .env 파일에 model_config에 정의되지 않은 변수가 있어도 무시하고 경고를 띄우지 않습니다.

# 설정 객체 생성
@lru_cache
def get_settings() -> Settings:
    return Settings()