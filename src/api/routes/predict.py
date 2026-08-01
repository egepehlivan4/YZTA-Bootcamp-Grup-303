"""FloraGuard — Uçtan Uca Tahmin Endpoint'i (Orkestratör Ajan girişi)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from src.agent.orchestrator import OrchestratorService
from src.api.dependencies import get_orchestrator
from src.config import Settings, get_settings
from src.data.schemas import PredictionResponse, Role, TokenPayload
from src.security.rbac import get_current_user

router = APIRouter(tags=["predict"])

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png"}


@router.post("", response_model=PredictionResponse)
async def predict(
    image: UploadFile = File(...),
    farmer_id: str = Form(...),
    location: str = Form(...),
    crop_type: str = Form("domates"),
    current_user: TokenPayload = Depends(get_current_user),
    orchestrator: OrchestratorService = Depends(get_orchestrator),
    settings: Settings = Depends(get_settings),
) -> PredictionResponse:
    """
    Yaprak fotoğrafını + konumu alır, Orkestratör Ajan üzerinden CNN + LSTM
    ensemble'ını ve regresyon modülünü tetikler, bağlamsallaştırılmış tavsiye üretir.

    RBAC: Çiftçi rolü yalnızca kendi farmer_id'si için analiz başlatabilir;
    Danışman/Admin herhangi bir çiftçi adına analiz başlatabilir.
    """
    if current_user.role == Role.FARMER and current_user.sub != farmer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Çiftçiler yalnızca kendi farmer_id'si için analiz başlatabilir.",
        )

    if image.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=415, detail="Yalnızca JPEG/PNG desteklenir.")

    tmp_path = settings.upload_tmp_dir / f"{uuid.uuid4().hex}_{image.filename}"
    tmp_path.write_bytes(await image.read())

    try:
        result = orchestrator.analyze(
            farmer_id=farmer_id, image_path=str(tmp_path), location=location, crop_type=crop_type,
        )
    except ValueError as exc:
        # CNN katmanı, içerik-tipi doğru ama baytları bozuk/geçersiz bir
        # görüntüde (ör. yarım yüklenmiş dosya) ValueError fırlatır — bunu
        # 500 yerine anlaşılır bir 422 yanıtına çeviriyoruz.
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    finally:
        tmp_path.unlink(missing_ok=True)

    return PredictionResponse(
        farmer_id=result["farmer_id"],
        disease_probability=result["disease_probability"],
        estimated_yield_loss_pct=result["estimated_yield_loss_pct"],
        advice=result["advice"],
        cnn_top_class=result["cnn_top_class"],
        model_version=settings.app_version,
        generated_at=datetime.now(timezone.utc),
    )
