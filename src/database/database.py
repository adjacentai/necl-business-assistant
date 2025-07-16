import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.database.models import Base, User

# Database URL for SQLite
DATABASE_URL = "sqlite+aiosqlite:///./database.db"

# Create an asynchronous engine
engine = create_async_engine(DATABASE_URL, echo=False)

# Create a configured "Session" class
async_session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def create_db_and_tables():
    """Initializes the database and creates tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_or_create_user(session: AsyncSession, user_id: int, user_name: str) -> User:
    """Gets a user from the database or creates one if it doesn't exist."""
    user = await session.get(User, user_id)
    if not user:
        user = User(user_id=user_id, user_name=user_name, message_count=1)
        session.add(user)
    else:
        user.message_count += 1
    
    await session.commit()
    return user 