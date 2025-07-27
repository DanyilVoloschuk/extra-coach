from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import event, text
from sqlalchemy.engine import Engine
from sqlite3 import Connection as SQLite3Connection

from infrastructure.config.settings import get_settings


# @event.listens_for(Engine, "connect")
# def _set_sqlite_pragma(dbapi_connection, connection_record):
#     if isinstance(dbapi_connection, SQLite3Connection):
#         cursor = dbapi_connection.cursor()
#         cursor.execute("PRAGMA foreign_keys=ON")
#         cursor.close()


def get_engine():
    settings = get_settings()

    # Note: You'll need to modify your DATABASE_URL to use async driver,
    # For example, postgresql+asyncpg:// instead of postgresql://
    connect_args = {"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}

    return create_async_engine(
        settings.DATABASE_URL,
        connect_args=connect_args,
        echo=settings.DEBUG if hasattr(settings, 'DEBUG') else False,
    )


engine = get_engine()
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    db = AsyncSessionLocal()
    try:
        yield db
    except Exception as e:
        await db.rollback()
        raise e
    finally:
        await db.close()



async def init_db() -> None:
    async with AsyncSessionLocal() as db:
        try:
            await db.execute(text("SELECT 1"))
        except Exception as e:
            print(f"Database connection failed: {e}")
            raise


def get_session():
    return AsyncSessionLocal