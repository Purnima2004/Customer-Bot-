from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings

Base = declarative_base()

engine: AsyncEngine = create_async_engine(
	settings.db_url,
	echo=False,
	future=True,
)

async_session_factory = sessionmaker(
	bind=engine,
	expire_on_commit=False,
	class_=AsyncSession,
	future=True,
)

async def get_db() -> AsyncSession:
	async with async_session_factory() as session:
		yield session

