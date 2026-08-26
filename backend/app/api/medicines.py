from fastapi import APIRouter, HTTPException

from app.schemas.models import Medicine
from app.services import data_store

router = APIRouter(prefix="/medicines", tags=["medicines"])


@router.get("", response_model=list[Medicine])
def list_medicines():
    return data_store.list_medicines()


@router.post("", response_model=Medicine, status_code=201)
def create_medicine(payload: Medicine):
    return data_store.create_medicine(payload)


@router.put("/{medicine_id}", response_model=Medicine)
def update_medicine(medicine_id: str, payload: Medicine):
    medicine = data_store.update_medicine(medicine_id, payload)
    if medicine:
        return medicine
    raise HTTPException(status_code=404, detail="药品不存在")


@router.delete("/{medicine_id}", status_code=204)
def remove_medicine(medicine_id: str):
    if data_store.remove_medicine(medicine_id):
        return None
    raise HTTPException(status_code=404, detail="药品不存在")
