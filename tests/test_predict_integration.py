"""
FloraGuard — Predict Endpoint Entegrasyon Testleri
Deterministik fallback pipeline ve (mock'lanmış) gerçek ajan tool-calling
yolu ile uçtan uca tahmin akışını doğrular.
"""

from __future__ import annotations

from io import BytesIO
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from src.api.main import create_app


@pytest.fixture
def client():
    app = create_app()
    with TestClient(app) as test_client:
        yield test_client


def _auth_headers(client: TestClient) -> dict[str, str]:
    response = client.post(
        "/api/auth/token",
        data={"username": "ciftci1", "password": "ciftci123"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _sample_image_bytes() -> bytes:
    image = Image.new("RGB", (256, 256), color=(34, 139, 34))
    buffer = BytesIO()
    image.save(buffer, format="JPEG")
    return buffer.getvalue()


def test_predict_endpoint_requires_auth(client: TestClient) -> None:
    response = client.post(
        "/api/predict",
        data={"farmer_id": "ciftci1", "location": "Antalya", "crop_type": "domates"},
        files={"image": ("leaf.jpg", _sample_image_bytes(), "image/jpeg")},
    )
    assert response.status_code == 401


@patch("src.agent.orchestrator.OrchestratorService._analyze_with_agent")
def test_predict_endpoint_returns_valid_response(mock_agent, client: TestClient) -> None:
    """LLM ajanı devre dışı bırakılarak deterministik pipeline test edilir."""
    mock_agent.side_effect = RuntimeError("agent disabled for test")

    response = client.post(
        "/api/predict",
        headers=_auth_headers(client),
        data={"farmer_id": "ciftci1", "location": "Antalya", "crop_type": "domates"},
        files={"image": ("leaf.jpg", _sample_image_bytes(), "image/jpeg")},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["farmer_id"] == "ciftci1"
    assert 0.0 <= data["disease_probability"] <= 1.0
    assert 0.0 <= data["estimated_yield_loss_pct"] <= 100.0
    assert data["advice"]
    assert data["cnn_top_class"]


def test_history_endpoint_path(client: TestClient) -> None:
    response = client.get("/api/history/ciftci1", headers=_auth_headers(client))
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_predict_endpoint_rejects_corrupt_image(client: TestClient) -> None:
    """
    Content-Type başlığı doğru (`image/jpeg`) ama baytları bozuk bir dosya
    yüklendiğinde API 500 yerine 422 ile anlaşılır bir hata dönmeli.
    """
    response = client.post(
        "/api/predict",
        headers=_auth_headers(client),
        data={"farmer_id": "ciftci1", "location": "Antalya", "crop_type": "domates"},
        files={"image": ("corrupt.jpg", b"bu gecerli bir goruntu degil", "image/jpeg")},
    )
    assert response.status_code == 422
    assert "detail" in response.json()


def test_predict_endpoint_uses_real_agent_tool_calling_path(client: TestClient, monkeypatch) -> None:
    """
    Orkestratör Ajan'ın (LangGraph/LLM) çıktısını doğru şekilde ayrıştırıp
    uçtan uca yanıt ürettiğini doğrular — `_agent.invoke` sahte (fake) bir
    LLM tool-calling sonucuyla mock'lanır, böylece gerçek Groq API anahtarı
    gerekmeden ajan yolu (deterministik fallback DEĞİL) test edilir.
    """
    fake_json = (
        '{"risk_score": 0.42, "estimated_yield_loss_pct": 12.5, '
        '"advice": "Ajan testinden gelen ozel tavsiye.", "cnn_top_class": "saglikli"}'
    )
    fake_agent = SimpleNamespace(invoke=lambda *args, **kwargs: {"messages": [SimpleNamespace(content=fake_json)]})
    monkeypatch.setattr(client.app.state.orchestrator, "_agent", fake_agent)

    response = client.post(
        "/api/predict",
        headers=_auth_headers(client),
        data={"farmer_id": "ciftci1", "location": "Antalya", "crop_type": "domates"},
        files={"image": ("leaf.jpg", _sample_image_bytes(), "image/jpeg")},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["disease_probability"] == pytest.approx(0.42)
    assert data["estimated_yield_loss_pct"] == pytest.approx(12.5)
    assert data["advice"] == "Ajan testinden gelen ozel tavsiye."
    assert data["cnn_top_class"] == "saglikli"
