"""
FloraGuard — Hava Durumu Veri Kaynağı
LSTM modelinin girdisi olan zaman serisini üretir.

OpenWeatherMap API anahtarı (`OPENWEATHER_API_KEY`) tanımlıysa gerçek hava
verisi çekilir; aksi halde konum adına göre deterministik sentetik seri
üretilir (demo/test tekrarlanabilirliği için).
"""

from __future__ import annotations

import hashlib
import logging
import os
from datetime import date

import requests

logger = logging.getLogger(__name__)

OPENWEATHER_GEO_URL = "https://api.openweathermap.org/geo/1.0/direct"
OPENWEATHER_FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"


def get_weather_series(location: str, days: int = 14) -> list[dict]:
    """LSTM/agent katmanları için standart hava serisi döner."""
    api_key = os.environ.get("OPENWEATHER_API_KEY")
    if api_key:
        try:
            return _fetch_openweather_series(location, days, api_key)
        except Exception:
            logger.exception(
                "OpenWeatherMap isteği başarısız; sentetik seriye düşülüyor (location=%s).",
                location,
            )
    return generate_synthetic_series(location, days)


def generate_synthetic_series(location: str, days: int = 14) -> list[dict]:
    """Konum + gün bazlı deterministik sentetik hava serisi."""
    seed = int(hashlib.sha256(f"{location.lower()}-{date.today()}".encode()).hexdigest(), 16) % (2**32)
    rng_state = seed

    def _next() -> float:
        nonlocal rng_state
        rng_state = (rng_state * 1103515245 + 12345) % (2**31)
        return rng_state / (2**31)

    series = []
    for day_offset in range(-days + 1, 1):
        temperature_c = 15 + _next() * 20
        humidity_pct = 40 + _next() * 55
        rainfall_mm = _next() ** 3 * 30
        series.append({
            "day_offset": day_offset,
            "temperature_c": round(temperature_c, 1),
            "humidity_pct": round(humidity_pct, 1),
            "rainfall_mm": round(rainfall_mm, 1),
        })
    return series


def _fetch_openweather_series(location: str, days: int, api_key: str) -> list[dict]:
    """OpenWeatherMap 5-day/3-hour forecast'ten günlük özet seri üretir."""
    geo_resp = requests.get(
        OPENWEATHER_GEO_URL,
        params={"q": location, "limit": 1, "appid": api_key},
        timeout=10,
    )
    geo_resp.raise_for_status()
    geo_data = geo_resp.json()
    if not geo_data:
        raise ValueError(f"Konum bulunamadı: {location}")

    lat, lon = geo_data[0]["lat"], geo_data[0]["lon"]
    forecast_resp = requests.get(
        OPENWEATHER_FORECAST_URL,
        params={"lat": lat, "lon": lon, "appid": api_key, "units": "metric"},
        timeout=10,
    )
    forecast_resp.raise_for_status()
    items = forecast_resp.json().get("list", [])
    if not items:
        raise ValueError(f"Forecast verisi boş: {location}")

    daily: dict[str, dict[str, list[float]]] = {}
    for item in items:
        day_key = item["dt_txt"][:10]
        bucket = daily.setdefault(day_key, {"temps": [], "humids": [], "rains": []})
        bucket["temps"].append(item["main"]["temp"])
        bucket["humids"].append(item["main"]["humidity"])
        bucket["rains"].append(item.get("rain", {}).get("3h", 0.0))

    sorted_days = sorted(daily.keys())[-days:]
    series = []
    for idx, day_key in enumerate(sorted_days):
        bucket = daily[day_key]
        series.append({
            "day_offset": idx - len(sorted_days) + 1,
            "temperature_c": round(sum(bucket["temps"]) / len(bucket["temps"]), 1),
            "humidity_pct": round(sum(bucket["humids"]) / len(bucket["humids"]), 1),
            "rainfall_mm": round(sum(bucket["rains"]), 1),
        })

    while len(series) < days:
        series.insert(0, {
            "day_offset": series[0]["day_offset"] - 1 if series else -days + 1,
            "temperature_c": series[0]["temperature_c"] if series else 20.0,
            "humidity_pct": series[0]["humidity_pct"] if series else 60.0,
            "rainfall_mm": 0.0,
        })

    return series[-days:]
