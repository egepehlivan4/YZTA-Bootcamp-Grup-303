"""
FloraGuard — Canlı Ortam Smoke Test

Uygulamanın deploy edildikten sonra temel akışların çalıştığını doğrular.
Bu test dosyası pytest ile çalıştırılabilir, ama canlı API URL'si gerektirir.

Kullanım:
    FLORAGUARD_LIVE_URL=https://floraguard-api.onrender.com pytest tests/test_smoke.py -v

Eğer FLORAGUARD_LIVE_URL tanımlı değilse testler atlanır (skip).
"""

import os

import pytest
import requests

LIVE_URL = os.environ.get("FLORAGUARD_LIVE_URL")
skip_if_no_live = pytest.mark.skipif(not LIVE_URL, reason="FLORAGUARD_LIVE_URL ortam değişkeni tanımlı değil")


@skip_if_no_live
def test_health_endpoint():
    """Canlı ortamda /health endpoint'inin başarıyla yanıt verdiğini doğrular."""
    response = requests.get(f"{LIVE_URL}/health", timeout=10)
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "floraguard-api"


@skip_if_no_live
def test_auth_login_flow():
    """Canlı ortamda demo kullanıcı ile giriş yapılabildiğini doğrular."""
    response = requests.post(
        f"{LIVE_URL}/api/auth/token",
        data={"username": "ciftci1", "password": "ciftci123"},
        timeout=10,
    )
    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert data["role"] == "farmer"


@skip_if_no_live
def test_protected_endpoint_requires_auth():
    """Canlı ortamda token olmadan korumalı endpoint'e erişimin reddedildiğini doğrular."""
    response = requests.get(f"{LIVE_URL}/api/history/ciftci1", timeout=10)
    assert response.status_code in (401, 403)


@skip_if_no_live
def test_end_to_end_history_flow():
    """Canlı ortamda login → geçmiş sorgulama akışının çalıştığını doğrular."""
    # 1. Login
    login_resp = requests.post(
        f"{LIVE_URL}/api/auth/token",
        data={"username": "ciftci1", "password": "ciftci123"},
        timeout=10,
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]

    # 2. Geçmiş sorgula
    history_resp = requests.get(
        f"{LIVE_URL}/api/history/ciftci1",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10,
    )
    assert history_resp.status_code == 200
    assert isinstance(history_resp.json(), list)
