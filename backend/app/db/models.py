from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.session import Base


class UserORM(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    openid: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    nickname: Mapped[str] = mapped_column(String(128), nullable=False, default="微信用户")
    avatar_url: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


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
    specification: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    manufacturer: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    approval_number: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    expire: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    risk: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    image_path: Mapped[str] = mapped_column(String(1024), nullable=False, default="")
    ocr_output_dir: Mapped[str] = mapped_column(String(1024), nullable=False, default="")


class MedicalRecordORM(Base):
    __tablename__ = "medical_records"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    title: Mapped[str] = mapped_column(String(128), nullable=False)
    date: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="待确认")
    content: Mapped[str] = mapped_column(Text, nullable=False, default="")


class MedicalRecordItemORM(Base):
    __tablename__ = "medical_record_items"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    record_id: Mapped[str] = mapped_column(
        ForeignKey("medical_records.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    label: Mapped[str] = mapped_column(String(128), nullable=False)
    value: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    unit: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    reference: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="normal")


class UploadAssetORM(Base):
    __tablename__ = "upload_assets"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    url: Mapped[str] = mapped_column(String(512), nullable=False)
    size: Mapped[int] = mapped_column(Integer, nullable=False)
    content_type: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class DrugLeafletORM(Base):
    __tablename__ = "drug_leaflets"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    generic_name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    brand_name: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    dosage_form: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    specification: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    manufacturer: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    approval_number: Mapped[str] = mapped_column(String(128), nullable=False, default="", index=True)
    source_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    source_type: Mapped[str] = mapped_column(String(32), nullable=False, default="url")
    raw_file_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    content_type: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    published_at: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending_review", index=True)
    reviewed_by: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    reviewed_at = mapped_column(DateTime(timezone=True), nullable=True)
    review_note: Mapped[str] = mapped_column(String(1024), nullable=False, default="")
    confirmed_by: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    confirmed_at = mapped_column(DateTime(timezone=True), nullable=True)
    index_status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")
    parser_version: Mapped[str] = mapped_column(String(32), nullable=False, default="leaflet-v1")


class DrugLeafletSectionORM(Base):
    __tablename__ = "drug_leaflet_sections"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    leaflet_id: Mapped[str] = mapped_column(
        ForeignKey("drug_leaflets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    section_name: Mapped[str] = mapped_column(String(128), nullable=False)
    section_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)