"""
FloraGuard — Hava Durumu Endpoint Testleri

Regresyon notu: `read_weather_series` route fonksiyonu, daha önce
`src.data.weather_source.get_weather_series` ile AYNI isme sahipti; bu isim
çakışması fonksiyonun kendi kendini çağırmasına (sonsuz özyineleme) yol
açıyordu ve endpoint canlı ortamda hiç yanıt vermiyordu. Bu test dosyası,
endpoint'in gerçekten 200 döndüğünü ve beklenen şemaya uyduğunu doğrulayarak
bu regresyonu kalıcı olarak yakalar.
"""

from __future__ import annotations

from fastapi.testclient import TestClient
import pytest

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
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_weather_requires_auth(client: TestClient) -> None:
    response = client.get("/api/weather/Antalya")
    assert response.status_code == 401


def test_weather_returns_series(client: TestClient) -> None:
    response = client.get("/api/weather/Antalya", headers=_auth_headers(client))

    assert response.status_code == 200
    data = response.json()
    assert data["location"] == "Antalya"
    assert len(data["series"]) == 14

    point = data["series"][0]
    assert {"day_offset", "temperature_c", "humidity_pct", "rainfall_mm"} <= point.keys()


def test_weather_series_is_deterministic_per_location(client: TestClient) -> None:
    headers = _auth_headers(client)
    first = client.get("/api/weather/Izmir", headers=headers).json()
    second = client.get("/api/weather/Izmir", headers=headers).json()
    assert first == second
