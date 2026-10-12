from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    pass


connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(settings.database_url, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def init_db() -> None:
    from app.db import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    if "medical_record_items" in inspect(engine).get_table_names():
        columns = {column["name"] for column in inspect(engine).get_columns("medical_record_items")}
        if "position" not in columns:
            with engine.begin() as connection:
                connection.execute(
                    text(
                        "ALTER TABLE medical_record_items "
                        "ADD COLUMN position INTEGER NOT NULL DEFAULT 0"
                    )
                )