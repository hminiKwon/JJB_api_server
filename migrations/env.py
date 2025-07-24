import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# ---------------------------------------------------------------------
# 1. 프로젝트 경로 설정 및 SQLAlchemy Base 임포트
#    (여러분의 프로젝트 구조에 맞게 'app.models.base' 경로를 수정하세요)
# ---------------------------------------------------------------------
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
sys.path.insert(0, project_root)

try:
    from app.models.user import User # <--- 이 부분을 여러분의 실제 Base import 경로로 변경하세요.
except ImportError:
    print("Warning: Could not import Base from app.models.base. "
          "Please ensure the path is correct in migrations/env.py.", file=sys.stderr)
    User = None

# ---------------------------------------------------------------------
# 2. Alembic 설정 로드 (alembic.ini 파일로부터)
# ---------------------------------------------------------------------
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ---------------------------------------------------------------------
# 3. SQLAlchemy Base.metadata 연결
# ---------------------------------------------------------------------
if User:
    target_metadata = User.metadata
else:
    target_metadata = None
    print("Error: target_metadata is None. Alembic auto-generation may not work correctly.", file=sys.stderr)

# ---------------------------------------------------------------------
# 4. 마이그레이션 실행 함수 정의 (온라인/오프라인 모드)
#    - 환경 변수에서 DATABASE_URL을 가져오도록 수정
# ---------------------------------------------------------------------

def run_migrations_offline() -> None:
    """
    구성된 엔진 없이 '오프라인' 모드에서 마이그레이션을 실행합니다.
    """
    # 환경 변수에서 DB URL을 가져옵니다.
    # 'DATABASE_URL'은 여러분이 설정한 환경 변수 이름으로 변경하세요.
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise ValueError("DATABASE_URL environment variable is not set for offline mode.")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    엔진이 있는 '온라인' 모드에서 마이그레이션을 실행합니다.
    """
    # 환경 변수에서 DB URL을 가져옵니다.
    # 'DATABASE_URL'은 여러분이 설정한 환경 변수 이름으로 변경하세요.
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL environment variable is not set for online mode.")

    connectable = engine_from_config(
        # config.get_section(...) 대신 직접 URL을 딕셔너리로 전달합니다.
        {"sqlalchemy.url": db_url}, # <-- 이 부분이 핵심 변경 사항
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

# ---------------------------------------------------------------------
# 5. 마이그레이션 모드 선택 및 실행
# ---------------------------------------------------------------------

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()