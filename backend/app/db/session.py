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
    if "medicines" in inspect(engine).get_table_names():
        columns = {column["name"] for column in inspect(engine).get_columns("medicines")}
        additions = {
            "specification": "VARCHAR(128) NOT NULL DEFAULT ''",
            "manufacturer": "VARCHAR(255) NOT NULL DEFAULT ''",
            "approval_number": "VARCHAR(128) NOT NULL DEFAULT ''",
            "image_path": "VARCHAR(1024) NOT NULL DEFAULT ''",
            "ocr_output_dir": "VARCHAR(1024) NOT NULL DEFAULT ''",
        }
        with engine.begin() as connection:
            for name, definition in additions.items():
                if name not in columns:
                    connection.execute(text(f"ALTER TABLE medicines ADD COLUMN {name} {definition}"))
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
    if "drug_leaflets" in inspect(engine).get_table_names():
        columns = {column["name"] for column in inspect(engine).get_columns("drug_leaflets")}
        additions = {
            "confirmed_by": "VARCHAR(64) NOT NULL DEFAULT ''",
            "confirmed_at": "DATETIME NULL",
            "index_status": "VARCHAR(32) NOT NULL DEFAULT 'pending'",
            "reviewed_by": "VARCHAR(64) NOT NULL DEFAULT ''",
            "reviewed_at": "DATETIME NULL",
            "review_note": "VARCHAR(1024) NOT NULL DEFAULT ''",
        }
        with engine.begin() as connection:
            for name, definition in additions.items():
                if name not in columns:
                    connection.execute(text(f"ALTER TABLE drug_leaflets ADD COLUMN {name} {definition}"))