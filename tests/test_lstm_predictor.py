"""
FloraGuard — LSTM Modeli Testleri
LSTMPredictor sınıfının ağırlıksız başlatılmasını, risk aralığı çıktısını ve boş seri doğrulamasını test eder.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from src.data.weather_source import generate_synthetic_series
from src.models.lstm_model import LSTMPredictor


def test_lstm_predictor_initializes_without_weights(tmp_path: Path) -> None:
    """
    Var olmayan bir ağırlık dosyası verildiğinde LSTMPredictor'ün sorunsuz başlatıldığını doğrular.
    """
    non_existent_weights = tmp_path / "non_existent_lstm.pt"
    predictor = LSTMPredictor(weights_path=non_existent_weights)
    assert predictor.model is not None


def test_lstm_predict_returns_risk_in_range(tmp_path: Path) -> None:
    """
    14 günlük hava durumu serisi verildiğinde risk_5d değerinin [0, 1] aralığında olduğunu doğrular.
    """
    predictor = LSTMPredictor(weights_path=tmp_path / "non_existent.pt")
    series = generate_synthetic_series("Antalya", days=14)

    result = predictor.predict(series)

    assert "risk_5d" in result
    assert isinstance(result["risk_5d"], float)
    assert 0.0 <= result["risk_5d"] <= 1.0


def test_lstm_predict_rejects_empty_series(tmp_path: Path) -> None:
    """
    Boş bir zaman serisi verildiğinde predict() metodunun ValueError fırlattığını doğrular.
    """
    predictor = LSTMPredictor(weights_path=tmp_path / "non_existent.pt")

    with pytest.raises(ValueError) as exc_info:
        predictor.predict([])

    assert "boş zaman serisi" in str(exc_info.value).lower()
