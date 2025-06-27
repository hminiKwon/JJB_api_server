# app/dependencies.py
import httpx
from contextlib import asynccontextmanager
from typing import AsyncGenerator

@asynccontextmanager
async def get_httpx_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """
    HTTPX AsyncClient를 제공하는 비동기 컨텍스트 매니저.
    요청 처리 전 클라이언트를 생성하고, 요청 처리 후 클라이언트를 닫습니다.
    """
    client = httpx.AsyncClient()
    try:
        yield client  # 이 시점에서 httpx.AsyncClient 인스턴스가 FastAPI 라우터로 주입됩니다.
    finally:
        # 요청 처리가 끝나면 클라이언트 연결 종료
        await client.aclose()