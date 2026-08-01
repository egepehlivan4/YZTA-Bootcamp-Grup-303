"""FloraGuard — Hava Durumu Endpoint'i (LSTM girdisi önizlemesi)."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from src.data.schemas import TokenPayload, WeatherSeries
from src.data.weather_source import get_weather_series
from src.security.rbac import get_current_user

router = APIRouter(tags=["weather"])


@router.get("/{location}", response_model=WeatherSeries)
def read_weather_series(location: str, _current_user: TokenPayload = Depends(get_current_user)) -> WeatherSeries:
    """LSTM modeline girdi olan son 14 günlük hava serisini döner (bkz. src/data/weather_source.py)."""
    series = get_weather_series(location)
    return WeatherSeries(location=location, series=series)
