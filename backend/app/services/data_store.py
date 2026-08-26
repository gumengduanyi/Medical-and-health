from app.schemas.models import HealthProfile, MedicalRecord, Medicine
from app.db.session import SessionLocal, init_db
from app.repositories.health_repository import HealthRepository, seed_defaults


def initialize() -> None:
    init_db()
    with SessionLocal() as session:
        seed_defaults(session)


initialize()


def get_profile() -> HealthProfile:
    with SessionLocal() as session:
        return HealthRepository(session).get_profile()


def save_profile(payload: HealthProfile) -> HealthProfile:
    with SessionLocal() as session:
        return HealthRepository(session).save_profile(payload)


def list_records() -> list[dict]:
    with SessionLocal() as session:
        return HealthRepository(session).list_records()


def create_record(payload: MedicalRecord) -> MedicalRecord:
    with SessionLocal() as session:
        return HealthRepository(session).create_record(payload)


def list_medicines() -> list[Medicine]:
    with SessionLocal() as session:
        return HealthRepository(session).list_medicines()


def create_medicine(payload: Medicine) -> Medicine:
    with SessionLocal() as session:
        return HealthRepository(session).create_medicine(payload)


def update_medicine(medicine_id: str, payload: Medicine) -> Medicine | None:
    with SessionLocal() as session:
        return HealthRepository(session).update_medicine(medicine_id, payload)


def remove_medicine(medicine_id: str) -> bool:
    with SessionLocal() as session:
        return HealthRepository(session).remove_medicine(medicine_id)