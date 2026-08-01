"""
FloraGuard — Konfigürasyon Sağlamlık Testleri

Regresyon notu: Varsayılan `llm_model` bir ara Groq tarafından kaldırılmış
(decommissioned) `llama3-70b-8192` değerine sabitlenmişti; bu, Orkestratör
Ajan'ın her istekte sessizce deterministik fallback'e düşmesine (yani
"gerçek ajan orkestrasyonu" hiç çalışmamasına) yol açıyordu. Bu test, bilinen
kaldırılmış model adının varsayılan olarak asla geri gelmediğini garanti eder.
"""

from __future__ import annotations

from src.config import Settings

KNOWN_DECOMMISSIONED_MODELS = {"llama3-70b-8192"}


def test_default_llm_model_is_not_decommissioned() -> None:
    settings = Settings(_env_file=None)
    assert settings.llm_model not in KNOWN_DECOMMISSIONED_MODELS
    assert settings.llm_model  # boş olmamalı


def test_ensemble_weights_sum_to_one() -> None:
    settings = Settings(_env_file=None)
    assert settings.ensemble_w_cnn + settings.ensemble_w_lstm == 1.0
