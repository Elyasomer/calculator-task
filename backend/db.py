from contextlib import asynccontextmanager, contextmanager
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker
import sqlalchemy as sa
from dotenv import load_dotenv
import os
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import mapped_column


load_dotenv()


def create_database_url(sync=False):
    POSTGRES_USER = os.environ.get("CALCULATOR_PG_USER")
    POSTGRES_PASSWORD = os.environ.get("CALCULATOR_PG_PASSWORD")
    POSTGRES_SERVER = os.environ.get("CALCULATOR_PG_SERVER", "localhost")
    POSTGRES_PORT = os.environ.get(
        "CALCULATOR_PG_PORT", 5432)  # default postgres port
    POSTGRES_DB = os.environ.get("CALCULATOR_PG_DB")
    if sync:
        return (
            f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@"
            + f"{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
        )
    return (
        f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@"
        + f"{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )


DATABASE_URL = create_database_url()
async_engine = create_async_engine(
    DATABASE_URL, future=True, echo=False)

sync_engine = create_engine(create_database_url(
    sync=True), future=True, echo=False)


async def get_session() -> AsyncSession:  # type: ignore
    async_session = sessionmaker(bind=async_engine,
                                 class_=AsyncSession,
                                 expire_on_commit=False)
    async with async_session() as session:
        yield session


@asynccontextmanager
async def get_async_session() -> AsyncSession:  # type: ignore
    async_session = sessionmaker(
        bind=async_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session


@contextmanager
def get_sync_session():
    with Session(sync_engine) as session:
        yield session


class Base(DeclarativeBase):
    pass


class Calculations(Base):
    __tablename__ = "calculations"

    id = sa.Column(sa.Integer(), primary_key=True)
    stmnt = sa.Column(sa.String(500), nullable=False)
    answer = sa.Column(sa.String(100), nullable=False)


Calculations.metadata.create_all(sync_engine)
