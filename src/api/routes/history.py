"""FloraGuard — Çiftçi Geçmişi Endpoint'i (agent hafızasının okuma/yazma ucu)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from src.agent.memory import FarmerMemory
from src.api.dependencies import get_memory
from src.config import Settings, get_settings
from src.data.schemas import HistoryRecord, HistoryRecordUpdate, TokenPayload
from src.security.rbac import can_modify_record, can_view_farmer_history, get_current_user
from src.security.users_db import get_user_role

router = APIRouter(tags=["history"])


@router.get("/{farmer_id}", response_model=list[HistoryRecord])
def get_history(
    farmer_id: str,
    limit: int = 20,
    current_user: TokenPayload = Depends(get_current_user),
    memory: FarmerMemory = Depends(get_memory),
    settings: Settings = Depends(get_settings),
) -> list[HistoryRecord]:
    """
    RBAC: Çiftçi yalnızca kendi geçmişini görür; Danışman kendi geçmişini ve
    çiftçilerin geçmişini görür (başka danışman/admin'inkini göremez);
    Admin herkesin geçmişini görür.
    """
    target_role = get_user_role(settings.db_path, farmer_id)
    if not can_view_farmer_history(current_user, farmer_id, target_role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu çiftçinin geçmişini görüntüleme yetkiniz yok.",
        )

    records = memory.get_recent_history(farmer_id, limit=limit)
    return [HistoryRecord(**record) for record in records]


@router.put("/record/{record_id}", response_model=HistoryRecord)
def update_history_record(
    record_id: int,
    payload: HistoryRecordUpdate,
    current_user: TokenPayload = Depends(get_current_user),
    memory: FarmerMemory = Depends(get_memory),
    settings: Settings = Depends(get_settings),
) -> HistoryRecord:
    """RBAC: Danışman yalnızca çiftçi kayıtlarını, Admin çiftçi+danışman kayıtlarını düzenleyebilir."""
    record = memory.get_record(record_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kayıt bulunamadı.")

    owner_role = get_user_role(settings.db_path, record["farmer_id"])
    if not can_modify_record(current_user, owner_role):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bu kaydı düzenleme yetkiniz yok.")

    updated = memory.update_record(
        record_id,
        crop_type=payload.crop_type,
        location=payload.location,
        advice=payload.advice,
    )
    if not updated:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Güncellenecek en az bir alan girin.")

    return HistoryRecord(**memory.get_record(record_id))


@router.delete("/record/{record_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
def delete_history_record(
    record_id: int,
    current_user: TokenPayload = Depends(get_current_user),
    memory: FarmerMemory = Depends(get_memory),
    settings: Settings = Depends(get_settings),
) -> None:
    """RBAC: Danışman yalnızca çiftçi kayıtlarını, Admin çiftçi+danışman kayıtlarını silebilir."""
    record = memory.get_record(record_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kayıt bulunamadı.")

    owner_role = get_user_role(settings.db_path, record["farmer_id"])
    if not can_modify_record(current_user, owner_role):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bu kaydı silme yetkiniz yok.")

    memory.delete_record(record_id)
