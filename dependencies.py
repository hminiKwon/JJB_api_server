# app/dependencies.py
import httpx
from contextlib import asynccontextmanager
from typing import AsyncGenerator

# 비동기 컨텍스트 매니저를 사용하여 httpx.AsyncClient 인스턴스를 관리
# 이 함수는 FastAPI의 Depends()를 통해 주입될 때마다 클라이언트를 제공합니다.
@asynccontextmanager
async def get_httpx_client_context() -> AsyncGenerator[httpx.AsyncClient, None]:
    """
    HTTPX AsyncClient를 제공하는 비동기 컨텍스트 매니저.
    요청 처리 전 클라이언트를 생성하고, 요청 처리 후 클라이언트를 닫습니다.
    """
    client = httpx.AsyncClient()
    try:
        yield client  # FastAPI에게 httpx.AsyncClient 인스턴스를 제공
    finally:
        await client.aclose() # 요청 처리가 끝나면 클라이언트 연결 종료