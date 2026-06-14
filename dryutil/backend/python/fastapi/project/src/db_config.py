import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Load env
load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL") #"postgresql+asyncpg://user:password@localhost:5432/mydb"
# For MySQL: mysql+aiomysql://user:password@localhost:3306/mydb
# For SQLite: sqlite+aiosqlite:///./test.db

engine = create_async_engine(DATABASE_URL, echo=True, future=True)

AsyncSessionLocal = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

Base = declarative_base()

# Dependency
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
