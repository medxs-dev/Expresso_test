# from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
# from sqlalchemy.orm import sessionmaker, declarative_base
# from app.core.config import settings

# DATABASE_URL = settings.DATABASE_URL

# engine = create_async_engine(DATABASE_URL, echo=True, future=True)
# SessionLocal = sessionmaker(
#     bind=engine, class_=AsyncSession, expire_on_commit=False, autoflush=False)

# Base = declarative_base()


# async def get_db():
#     try:
#         async with SessionLocal() as session:
#             yield session
#     finally:
#         await session.close()


# async def create_table():
#     print("Creating tables...")
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
#     print("Tables created successfully!")


import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

DATABASE_URL = settings.DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=True, future=True)

SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

Base = declarative_base()


async def get_db():
    async with SessionLocal() as session:
        yield session


# Optional: Use logging for better observability
logger = logging.getLogger(__name__)


async def create_table():
    logger.info("Creating tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Tables created successfully!")
