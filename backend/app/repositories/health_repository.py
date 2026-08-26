from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import HealthProfileORM, MedicalRecordORM, MedicineORM
from app.schemas.models import HealthProfile, MedicalRecord, Medicine


def _profile_to_schema(row: HealthProfileORM) -> HealthProfile:
    return HealthProfile(
        id=row.id,
        name=row.name,
        sex=row.sex,
        age=row.age,
        height=row.height,
        weight=row.weight,
        allergy=row.allergy,
        disease=row.disease,
        familyHistory=row.family_history,
    )


def _medicine_to_schema(row: MedicineORM) -> Medicine:
    return Medicine(
        id=row.id,
        name=row.name,
        dose=row.dose,
        stock=row.stock,
        expire=row.expire,
        risk=row.risk,
    )


def _record_to_schema(row: MedicalRecordORM) -> MedicalRecord:
    return MedicalRecord(
        id=row.id,
        title=row.title,
        date=row.date,
        status=row.status,
        content=row.content,
    )


def seed_defaults(session: Session) -> None:
    if session.get(HealthProfileORM, "profile_001") is None:
        session.add(
            HealthProfileORM(
                id="profile_001",
                name="王先生",
                sex="男",
                age=60,
                height=172,
                weight=68,
                allergy="无",
                disease="高血压",
                family_history="无",
            )
        )

    if session.get(MedicineORM, "med_001") is None:
        session.add_all(
            [
                MedicineORM(
                    id="med_001",
                    name="阿司匹林肠溶片",
                    dose="0.1g × 1片｜饭后服用",
                    stock=15,
                    expire="2027-12-10",
                    risk="库存偏低，建议补货",
                ),
                MedicineORM(
                    id="med_002",
                    name="强力枇杷露",
                    dose="10ml × 3次｜摇匀后服用",
                    stock=80,
                    expire="2026-05-20",
                    risk="即将过期，优先使用",
                ),
            ]
        )

    if session.get(MedicalRecordORM, "record_001") is None:
        session.add_all(
            [
                MedicalRecordORM(
                    id="record_001",
                    title="年度体检报告",
                    date="2026-04-18",
                    status="已入库",
                    content="年度体检报告显示血压 145/96，空腹血糖 6.8，建议关注血压和血糖趋势。",
                ),
                MedicalRecordORM(
                    id="record_002",
                    title="血常规化验单",
                    date="2026-03-22",
                    status="已分析",
                    content="血常规化验单显示白细胞、血红蛋白等指标正常。",
                ),
            ]
        )

    session.commit()


class HealthRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_profile(self) -> HealthProfile:
        row = self.session.scalar(select(HealthProfileORM).limit(1))
        if row is None:
            payload = HealthProfile()
            return self.save_profile(payload)
        return _profile_to_schema(row)

    def save_profile(self, payload: HealthProfile) -> HealthProfile:
        row = HealthProfileORM(
            id=payload.id,
            name=payload.name,
            sex=payload.sex,
            age=payload.age,
            height=payload.height,
            weight=payload.weight,
            allergy=payload.allergy,
            disease=payload.disease,
            family_history=payload.family_history,
        )
        self.session.merge(row)
        self.session.commit()
        return payload

    def list_records(self) -> list[dict]:
        rows = self.session.scalars(
            select(MedicalRecordORM).order_by(MedicalRecordORM.date.desc(), MedicalRecordORM.id.desc())
        ).all()
        return [
            {"id": row.id, "title": row.title, "date": row.date, "status": row.status, "content": row.content}
            for row in rows
        ]

    def create_record(self, payload: MedicalRecord) -> MedicalRecord:
        record = payload.model_copy(
            update={"id": payload.id or f"record_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"}
        )
        row = MedicalRecordORM(
            id=record.id,
            title=record.title,
            date=record.date,
            status=record.status,
            content=record.content,
        )
        self.session.add(row)
        self.session.commit()
        return _record_to_schema(row)

    def list_medicines(self) -> list[Medicine]:
        rows = self.session.scalars(select(MedicineORM).order_by(MedicineORM.id.desc())).all()
        return [_medicine_to_schema(row) for row in rows]

    def create_medicine(self, payload: Medicine) -> Medicine:
        medicine = payload.model_copy(
            update={"id": payload.id or f"med_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"}
        )
        row = MedicineORM(
            id=medicine.id,
            name=medicine.name,
            dose=medicine.dose,
            stock=medicine.stock,
            expire=medicine.expire,
            risk=medicine.risk,
        )
        self.session.add(row)
        self.session.commit()
        return medicine

    def update_medicine(self, medicine_id: str, payload: Medicine) -> Medicine | None:
        row = self.session.get(MedicineORM, medicine_id)
        if row is None:
            return None
        row.name = payload.name
        row.dose = payload.dose
        row.stock = payload.stock
        row.expire = payload.expire
        row.risk = payload.risk
        self.session.commit()
        return _medicine_to_schema(row)

    def remove_medicine(self, medicine_id: str) -> bool:
        row = self.session.get(MedicineORM, medicine_id)
        if row is None:
            return False
        self.session.delete(row)
        self.session.commit()
        return True