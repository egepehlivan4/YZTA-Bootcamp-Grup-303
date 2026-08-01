"""
FloraGuard — Orkestratör Ajan
LangGraph'ın `create_react_agent` yardımcı fonksiyonuyla kurulan tool-calling
ajanı. Ajan; CNN, LSTM, Ensemble, Regresyon ve Hafıza modüllerini sırayla
tool olarak çağırır, ardından bağlamsallaştırılmış bir tavsiye üretir.

Güvenilirlik notu: LLM'ler bazen istenen JSON şemasına tam uymayabilir.
Bu yüzden `OrchestratorService.analyze()`, LLM çıktısını ayrıştıramazsa
DETERMİNİSTİK bir fallback pipeline'a (tool'ları doğrudan sırayla çağırma)
düşer — API asla LLM'in kaprisine bağlı olarak çökmez, sadece tavsiye metni
şablona döner.
"""

from __future__ import annotations

import json
import logging
import re

from langchain_groq import ChatGroq

try:
    from langgraph.prebuilt import create_react_agent  # LangGraph >=1.0
except ImportError:
    from langchain.agents import create_agent as create_react_agent  # fallback

from src.agent.memory import FarmerMemory
from src.agent.prompts import HUMAN_TASK_TEMPLATE, SYSTEM_PROMPT
from src.agent.tools import build_tools
from src.config import Settings
from src.models.cnn_model import CNNPredictor
from src.models.ensemble import EnsembleWeights, combine_risk_scores
from src.models.lstm_model import LSTMPredictor
from src.models.regression import YieldLossRegressor

logger = logging.getLogger(__name__)

_JSON_BLOCK_RE = re.compile(r"\{.*\}", re.DOTALL)


class OrchestratorService:
    """API katmanının konuştuğu tek giriş noktası (facade)."""

    def __init__(
        self,
        settings: Settings,
        cnn_predictor: CNNPredictor,
        lstm_predictor: LSTMPredictor,
        regressor: YieldLossRegressor,
        memory: FarmerMemory,
    ):
        self.settings = settings
        self.cnn_predictor = cnn_predictor
        self.lstm_predictor = lstm_predictor
        self.regressor = regressor
        self.memory = memory
        self.ensemble_weights = EnsembleWeights(settings.ensemble_w_cnn, settings.ensemble_w_lstm)

        self.tools = build_tools(cnn_predictor, lstm_predictor, regressor, memory, self.ensemble_weights)
        self._agent = self._build_agent()

    def _build_agent(self):
        # api_key açıkça verilmezse ChatGroq otomatik olarak GROQ_API_KEY
        # ortam değişkenini okur; None'ı açıkça geçmek bu davranışı ezip hataya yol açar.
        llm_kwargs = {"model": self.settings.llm_model, "temperature": self.settings.llm_temperature}
        if self.settings.groq_api_key:
            llm_kwargs["api_key"] = self.settings.groq_api_key
        llm = ChatGroq(**llm_kwargs)
        return create_react_agent(llm, self.tools, prompt=SYSTEM_PROMPT)

    def analyze(self, farmer_id: str, image_path: str, location: str, crop_type: str) -> dict:
        try:
            return self._analyze_with_agent(farmer_id, image_path, location, crop_type)
        except Exception:
            logger.exception("Agent tabanlı analiz başarısız oldu; deterministik pipeline'a düşülüyor.")
            return self._analyze_deterministic(farmer_id, image_path, location, crop_type)

    # -- Ana yol: LLM ajanı tool'ları kendisi orkestre eder -----------------
    def _analyze_with_agent(self, farmer_id: str, image_path: str, location: str, crop_type: str) -> dict:
        human_message = HUMAN_TASK_TEMPLATE.format(
            farmer_id=farmer_id, image_path=image_path, location=location, crop_type=crop_type,
        )
        result = self._agent.invoke(
            {"messages": [("user", human_message)]},
            config={"recursion_limit": self.settings.agent_max_iterations},
        )
        final_content = result["messages"][-1].content
        parsed = self._parse_json_response(final_content)

        return {
            "farmer_id": farmer_id,
            "disease_probability": float(parsed["risk_score"]),
            "estimated_yield_loss_pct": float(parsed["estimated_yield_loss_pct"]),
            "advice": str(parsed["advice"]),
            "cnn_top_class": str(parsed.get("cnn_top_class", "bilinmiyor")),
        }

    @staticmethod
    def _parse_json_response(content: str) -> dict:
        match = _JSON_BLOCK_RE.search(content)
        if not match:
            raise ValueError(f"Ajan yanıtında JSON bulunamadı: {content!r}")
        return json.loads(match.group(0))

    # -- Fallback yol: LLM olmadan, tool'ların altındaki mantığı doğrudan çağır --
    def _analyze_deterministic(self, farmer_id: str, image_path: str, location: str, crop_type: str) -> dict:
        from pathlib import Path

        from src.data.weather_source import generate_synthetic_series

        cnn_result = self.cnn_predictor.predict(Path(image_path).read_bytes())
        top_class = max(cnn_result["class_probabilities"], key=cnn_result["class_probabilities"].get)

        weather_series = generate_synthetic_series(location)
        lstm_result = self.lstm_predictor.predict(weather_series)

        ensemble_result = combine_risk_scores(
            cnn_result["diseased_probability"], lstm_result["risk_5d"], self.ensemble_weights,
        )
        yield_result = self.regressor.predict(ensemble_result["risk_score"], crop_type)

        history_summary = self.memory.summarize_for_agent(farmer_id)
        advice = (
            f"Önümüzdeki 5 gün içinde %{ensemble_result['risk_score'] * 100:.0f} hastalık riski var "
            f"(tahmini verim kaybı: %{yield_result['estimated_yield_loss_pct']:.1f}). "
            f"Nem ve sulama düzeyini gözden geçirin. ({history_summary.splitlines()[0]})"
        )

        self.memory.add_record(
            farmer_id=farmer_id, crop_type=crop_type, location=location,
            disease_probability=ensemble_result["risk_score"],
            estimated_yield_loss_pct=yield_result["estimated_yield_loss_pct"], advice=advice,
        )

        return {
            "farmer_id": farmer_id,
            "disease_probability": ensemble_result["risk_score"],
            "estimated_yield_loss_pct": yield_result["estimated_yield_loss_pct"],
            "advice": advice,
            "cnn_top_class": top_class,
        }
