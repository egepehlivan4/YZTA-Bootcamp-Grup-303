"""
FloraGuard — API Health & Auth Endpoint Testleri
FastAPI TestClient kullanarak API uç noktalarının durumunu ve kimlik doğrulama akışını test eder.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from src.api.main import create_app


@pytest.fixture
def client():
    """TestClient nesnesi oluşturan ve uygulama lifespan döngüsünü çalıştıran pytest fixture."""
    app = create_app()
    with TestClient(app) as test_client:
        yield test_client


def test_health(client: TestClient) -> None:
    """
    /health endpoint'inin HTTP 200 ve beklenen JSON yapısını döndürdüğünü doğrulayan test.
    """
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "floraguard-api"
    assert "version" in data
    assert "environment" in data


def test_auth_token_valid_credentials(client: TestClient) -> None:
    """
    Geçerli demo bilgileri (ciftci1/ciftci123) ile token isteğinde HTTP 200 ve
    JWT token döndüğünü doğrulayan test.
    """
    response = client.post(
        "/api/auth/token",
        data={"username": "ciftci1", "password": "ciftci123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["role"] == "farmer"


def test_auth_token_wrong_password(client: TestClient) -> None:
    """
    Hatalı şifre girildiğinde HTTP 401 Unauthorized döndüğünü doğrulayan test.
    """
    response = client.post(
        "/api/auth/token",
        data={"username": "ciftci1", "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert "detail" in response.json()


def test_history_unauthenticated_returns_401(client: TestClient) -> None:
    """
    Yetkilendirme token'ı olmadan korumalı geçmiş endpoint'ine erişim denendiğinde
    HTTP 401 döndüğünü doğrulayan test.
    """
    response = client.get("/api/history/ciftci1")
    assert response.status_code == 401
