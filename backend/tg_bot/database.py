from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from config import config

# Асинхронный движок БД
engine = create_async_engine(config.DATABASE_URL)

# Фабрика сессий
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

async def get_db() -> AsyncSession:
    """Генератор асинхронных сессий для работы с БД"""
    async with AsyncSessionLocal() as session:
        yield session