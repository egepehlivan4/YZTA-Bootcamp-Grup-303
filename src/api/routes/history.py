"""FloraGuard — Çiftçi Geçmişi Endpoint'i (agent hafızasının okuma ucu)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from src.agent.memory import FarmerMemory
from src.api.dependencies import get_memory
from src.data.schemas import HistoryRecord, Role, TokenPayload
from src.security.rbac import get_current_user

router = APIRouter(tags=["history"])


@router.get("/{farmer_id}", response_model=list[HistoryRecord])
def get_history(
    farmer_id: str,
    limit: int = 20,
    current_user: TokenPayload = Depends(get_current_user),
    memory: FarmerMemory = Depends(get_memory),
) -> list[HistoryRecord]:
    """RBAC: Çiftçi yalnızca kendi geçmişini görür; Danışman/Admin herkesinkini görebilir."""
    if current_user.role == Role.FARMER and current_user.sub != farmer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Çiftçiler yalnızca kendi geçmişini görüntüleyebilir.",
        )

    records = memory.get_recent_history(farmer_id, limit=limit)
    return [HistoryRecord(**record) for record in records]
