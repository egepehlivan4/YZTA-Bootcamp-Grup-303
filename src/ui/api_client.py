"""
FloraGuard — Streamlit için Backend API İstemcisi
Tüm HTTP çağrıları bu modülden geçer (DRY); Streamlit widget'ları hiçbir
zaman doğrudan `requests` kullanmaz. Bu ayrım, arayüz kodunu ağ hatalarından
ve HTTP detaylarından izole eder (katmanlı mimari — bkz. README).
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import requests

API_BASE_URL = os.environ.get("FLORAGUARD_API_URL", "http://localhost:8000")

DEFAULT_TIMEOUT_S = 15
PREDICT_TIMEOUT_S = 120  # Ajan (LLM tool-calling) yanıtı için daha uzun süre tanınır.


class ApiError(Exception):
    """Backend'e ulaşılamadığında veya sunucu hata döndüğünde fırlatılır."""


@dataclass
class ApiResponse:
    ok: bool
    status_code: int | None
    data: Any = None
    message: str = ""


def _extract_error_message(response: requests.Response) -> str:
    """FastAPI'nin standart `{"detail": "..."}` hata gövdesinden okunabilir mesaj çıkarır."""
    try:
        payload = response.json()
        detail = payload.get("detail")
        if isinstance(detail, str):
            return detail
        if detail is not None:
            return str(detail)
    except ValueError:
        pass
    return response.text or f"Beklenmeyen hata (HTTP {response.status_code})"


def _request(method: str, endpoint: str, *, timeout: int = DEFAULT_TIMEOUT_S, **kwargs: Any) -> ApiResponse:
    url = f"{API_BASE_URL}{endpoint}"
    try:
        response = requests.request(method, url, timeout=timeout, **kwargs)
    except requests.ConnectionError:
        return ApiResponse(
            ok=False, status_code=None,
            message=f"Backend sunucusuna ulaşılamadı ({url}). Uygulama lokalde ise uvicorn'un çalıştığından emin olun.",
        )
    except requests.Timeout:
        return ApiResponse(
            ok=False, status_code=None,
            message="API isteği zaman aşımına uğradı. Model veya ajan çok yavaş yanıt veriyor olabilir.",
        )

    if response.status_code >= 400:
        return ApiResponse(ok=False, status_code=response.status_code, message=_extract_error_message(response))

    return ApiResponse(ok=True, status_code=response.status_code, data=response.json())


def login(username: str, password: str) -> ApiResponse:
    return _request("POST", "/api/auth/token", data={"username": username, "password": password})


def predict(
    access_token: str,
    *,
    farmer_id: str,
    location: str,
    crop_type: str,
    image_name: str,
    image_bytes: bytes,
    image_type: str,
) -> ApiResponse:
    return _request(
        "POST",
        "/api/predict",
        timeout=PREDICT_TIMEOUT_S,
        headers={"Authorization": f"Bearer {access_token}"},
        files={"image": (image_name, image_bytes, image_type)},
        data={"farmer_id": farmer_id, "location": location, "crop_type": crop_type},
    )


def get_history(access_token: str, farmer_id: str, limit: int = 20) -> ApiResponse:
    return _request(
        "GET",
        f"/api/history/{farmer_id}",
        params={"limit": limit},
        headers={"Authorization": f"Bearer {access_token}"},
    )
