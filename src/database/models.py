from sqlalchemy import BigInteger, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func as sql_func


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""
    created_at = mapped_column(sql_func.now(), server_default=sql_func.now())
    updated_at = mapped_column(sql_func.now(), server_default=sql_func.now(), onupdate=sql_func.now())


class User(Base):
    """Represents a user in the database."""
    __tablename__ = 'users'

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    user_name: Mapped[str] = mapped_column(String(255), nullable=True)
    message_count: Mapped[int] = mapped_column(default=0) 