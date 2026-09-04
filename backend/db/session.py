import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from dotenv import load_dotenv
from db.models import Base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./tathyaai.db")

# Fallback to SQLite if PostgreSQL connection fails or URL is SQLite
if "sqlite" in DATABASE_URL:
  engine = create_async_engine(DATABASE_URL, echo=False)
else:
  try:
    engine = create_async_engine(DATABASE_URL, echo=False)
  except Exception:
    DATABASE_URL = "sqlite+aiosqlite:///./tathyaai.db"
    engine = create_async_engine(DATABASE_URL, echo=False)

async_session_factory = async_sessionmaker(engine, expire_on_commit=False)

async def init_db():
  async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)

async def get_db():
  async with async_session_factory() as session:
    yield session