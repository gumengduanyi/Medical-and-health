from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.session import Base


class HealthProfileORM(Base):
    __tablename__ = "health_profiles"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    sex: Mapped[str] = mapped_column(String(16), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    height: Mapped[int] = mapped_column(Integer, nullable=False)
    weight: Mapped[int] = mapped_column(Integer, nullable=False)
    allergy: Mapped[str] = mapped_column(String(255), nullable=False, default="无")
    disease: Mapped[str] = mapped_column(String(255), nullable=False, default="无")
    family_history: Mapped[str] = mapped_column(String(255), nullable=False, default="无")


class MedicineORM(Base):
    __tablename__ = "medicines"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    dose: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    expire: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    risk: Mapped[str] = mapped_column(String(255), nullable=False, default="")


class MedicalRecordORM(Base):
    __tablename__ = "medical_records"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    title: Mapped[str] = mapped_column(String(128), nullable=False)
    date: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="待确认")
    content: Mapped[str] = mapped_column(Text, nullable=False, default="")


class UploadAssetORM(Base):
    __tablename__ = "upload_assets"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    url: Mapped[str] = mapped_column(String(512), nullable=False)
    size: Mapped[int] = mapped_column(Integer, nullable=False)
    content_type: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())