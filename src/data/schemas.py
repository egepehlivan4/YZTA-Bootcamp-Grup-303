"""
FloraGuard — Paylaşılan Pydantic Şemaları
API, agent ve UI katmanları arasındaki "ortak dil". Tek yerde tanımlanır,
her yerde import edilir (DRY) — böylece API sözleşmesi tek kaynaktan yönetilir.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class Role(str, Enum):
    FARMER = "farmer"
    ADVISOR = "advisor"
    ADMIN = "admin"


# ---------------------------------------------------------------------------
# Kimlik doğrulama
# ---------------------------------------------------------------------------

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: Role


class TokenPayload(BaseModel):
    sub: str  # username
    role: Role
    exp: int


# ---------------------------------------------------------------------------
# Model / Ensemble / Regresyon çıktıları
# ---------------------------------------------------------------------------

class WeatherPoint(BaseModel):
    day_offset: int = Field(..., description="Bugüne göre gün (-13 .. 0 gibi geçmiş kayıtlar)")
    temperature_c: float
    humidity_pct: float
    rainfall_mm: float


class WeatherSeries(BaseModel):
    location: str
    series: list[WeatherPoint]


class CNNResult(BaseModel):
    class_probabilities: dict[str, float]
    diseased_probability: float


class LSTMResult(BaseModel):
    risk_5d: float = Field(..., description="Önümüzdeki 5 gün için 0-1 arası hastalık riski")


class EnsembleResult(BaseModel):
    risk_score: float = Field(..., ge=0.0, le=1.0)
    cnn_component: float
    lstm_component: float
    w_cnn: float
    w_lstm: float


class YieldLossResult(BaseModel):
    estimated_yield_loss_pct: float = Field(..., ge=0.0, le=100.0)
    model_used: str


# ---------------------------------------------------------------------------
# Uçtan uca tahmin
# ---------------------------------------------------------------------------

class PredictionRequestMeta(BaseModel):
    farmer_id: str
    location: str
    crop_type: str = "domates"


class PredictionResponse(BaseModel):
    farmer_id: str
    disease_probability: float = Field(..., description="Ensemble sonrası 5 günlük hastalık riski (0-1)")
    estimated_yield_loss_pct: float
    advice: str
    cnn_top_class: str
    model_version: str
    generated_at: datetime


class HistoryRecordUpdate(BaseModel):
    """Danışman/Admin tarafından düzenlenebilir alanlar — model çıktıları
    (disease_probability, estimated_yield_loss_pct) kasıtlı olarak dışarıda
    bırakılmıştır (bkz. FarmerMemory.update_record)."""

    crop_type: str | None = None
    location: str | None = None
    advice: str | None = None


class HistoryRecord(BaseModel):
    id: int | None = None
    farmer_id: str
    timestamp: datetime
    disease_probability: float
    estimated_yield_loss_pct: float
    crop_type: str
    location: str
    advice: str | None = None
