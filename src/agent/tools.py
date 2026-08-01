"""
FloraGuard — Agent Tool Tanımları
CNN, LSTM, Ensemble, Regresyon ve Hafıza modüllerini LangChain `StructuredTool`
olarak sarmalar. Orkestratör Ajan (orchestrator.py) bu tool listesini bir
LangGraph ReAct ajanına verir; LLM hangi tool'u ne zaman çağıracağına kendisi
karar verir (bkz. prompts.py'deki sistem talimatı).

Tasarım kararı: Tool'lar bağımsız singleton'lar DEĞİL — `build_tools(...)`
fabrikası, önceden oluşturulmuş model/hafıza nesnelerini closure ile tool'lara
enjekte eder. Bu, testlerde sahte (fake) model nesneleriyle tool'ları izole
şekilde test etmeyi mümkün kılar ve global durum bağımlılığını önler.
"""

from __future__ import annotations

from pathlib import Path

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from src.agent.memory import FarmerMemory
from src.data.weather_source import get_weather_series
from src.models.cnn_model import CNNPredictor
from src.models.ensemble import EnsembleWeights, combine_risk_scores
from src.models.lstm_model import LSTMPredictor
from src.models.regression import YieldLossRegressor


# ---------------------------------------------------------------------------
# Girdi şemaları (LLM'in tool çağrısı üretirken uyacağı JSON şeması)
# ---------------------------------------------------------------------------

class AnalyzeLeafInput(BaseModel):
    image_path: str = Field(..., description="Sunucuda geçici olarak kaydedilmiş yaprak görüntüsünün dosya yolu.")


class AnalyzeWeatherRiskInput(BaseModel):
    location: str = Field(..., description="Çiftliğin konumu (şehir/ilçe adı).")


class ComputeEnsembleInput(BaseModel):
    cnn_diseased_probability: float = Field(..., description="analyze_leaf_image sonucundaki diseased_probability.")
    lstm_risk_5d: float = Field(..., description="analyze_weather_risk sonucundaki risk_5d.")


class EstimateYieldLossInput(BaseModel):
    risk_score: float = Field(..., description="compute_ensemble_risk sonucundaki risk_score.")
    crop_type: str = Field(default="domates", description="Ürün tipi (domates, biber, salatalik, patates, bugday).")


class FarmerHistoryInput(BaseModel):
    farmer_id: str = Field(..., description="Çiftçinin benzersiz kimliği.")
    limit: int = Field(default=5, description="Getirilecek maksimum geçmiş kayıt sayısı.")


class SaveRecordInput(BaseModel):
    farmer_id: str
    crop_type: str
    location: str
    disease_probability: float
    estimated_yield_loss_pct: float
    advice: str


# ---------------------------------------------------------------------------
# Tool fabrikası
# ---------------------------------------------------------------------------

def build_tools(
    cnn_predictor: CNNPredictor,
    lstm_predictor: LSTMPredictor,
    regressor: YieldLossRegressor,
    memory: FarmerMemory,
    ensemble_weights: EnsembleWeights,
) -> list[StructuredTool]:
    """Enjekte edilmiş bağımlılıklarla tam tool listesini üretir."""

    def _analyze_leaf_image(image_path: str) -> dict:
        image_bytes = Path(image_path).read_bytes()
        return cnn_predictor.predict(image_bytes)

    def _analyze_weather_risk(location: str) -> dict:
        series = get_weather_series(location)
        result = lstm_predictor.predict(series)
        result["location"] = location
        result["days_analyzed"] = len(series)
        return result

    def _compute_ensemble_risk(cnn_diseased_probability: float, lstm_risk_5d: float) -> dict:
        return combine_risk_scores(cnn_diseased_probability, lstm_risk_5d, ensemble_weights)

    def _estimate_yield_loss(risk_score: float, crop_type: str = "domates") -> dict:
        return regressor.predict(risk_score, crop_type)

    def _get_farmer_history(farmer_id: str, limit: int = 5) -> str:
        return memory.summarize_for_agent(farmer_id, limit=limit)

    def _save_prediction_record(
        farmer_id: str, crop_type: str, location: str,
        disease_probability: float, estimated_yield_loss_pct: float, advice: str,
    ) -> str:
        record_id = memory.add_record(
            farmer_id=farmer_id, crop_type=crop_type, location=location,
            disease_probability=disease_probability,
            estimated_yield_loss_pct=estimated_yield_loss_pct, advice=advice,
        )
        return f"Kayıt hafızaya eklendi (id={record_id})."

    return [
        StructuredTool.from_function(
            func=_analyze_leaf_image,
            name="analyze_leaf_image",
            description="Yaprak fotoğrafını CNN modelinden geçirir; sınıf olasılıklarını ve hastalık olasılığını döner.",
            args_schema=AnalyzeLeafInput,
        ),
        StructuredTool.from_function(
            func=_analyze_weather_risk,
            name="analyze_weather_risk",
            description="Konuma göre son 14 günlük hava serisini alır ve LSTM ile 5 günlük hastalık riskini hesaplar.",
            args_schema=AnalyzeWeatherRiskInput,
        ),
        StructuredTool.from_function(
            func=_compute_ensemble_risk,
            name="compute_ensemble_risk",
            description="CNN hastalık olasılığı ile LSTM riskini ağırlıklı ortalamayla tek bir risk skorunda birleştirir.",
            args_schema=ComputeEnsembleInput,
        ),
        StructuredTool.from_function(
            func=_estimate_yield_loss,
            name="estimate_yield_loss",
            description="Ensemble risk skorundan ve ürün tipinden tahmini %verim kaybını hesaplar (regresyon modeli).",
            args_schema=EstimateYieldLossInput,
        ),
        StructuredTool.from_function(
            func=_get_farmer_history,
            name="get_farmer_history",
            description="Çiftçinin geçmiş tahmin kayıtlarını (tarih, risk, verim kaybı) özet metin olarak döner.",
            args_schema=FarmerHistoryInput,
        ),
        StructuredTool.from_function(
            func=_save_prediction_record,
            name="save_prediction_record",
            description="Üretilen analiz sonucunu ve tavsiyeyi çiftçinin hafızasına (geçmişine) kaydeder.",
            args_schema=SaveRecordInput,
        ),
    ]
