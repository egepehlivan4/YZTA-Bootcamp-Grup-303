"""
FloraGuard — Hava Durumu Sentetik Veri Kaynağı Testleri
generate_synthetic_series fonksiyonunun uzunluk, deterministiktik, anahtar varlığı ve değer aralıklarını test eder.
"""

from __future__ import annotations

import pytest

from src.data.weather_source import generate_synthetic_series


def test_synthetic_series_length() -> None:
    """
    Döndürülen serinin eleman sayısının 'days' parametresine eşit olduğunu doğrular.
    """
    series_7 = generate_synthetic_series("Antalya", days=7)
    assert len(series_7) == 7

    series_14 = generate_synthetic_series("Izmir", days=14)
    assert len(series_14) == 14


def test_synthetic_series_deterministic() -> None:
    """
    Aynı konum ve aynı gün için üretilen serinin tamamen aynı (deterministik) olduğunu doğrular.
    """
    series_a1 = generate_synthetic_series("Antalya", days=14)
    series_a2 = generate_synthetic_series("Antalya", days=14)
    assert series_a1 == series_a2

    # Farklı konumlar farklı sonuçlar üretmeli
    series_b = generate_synthetic_series("Konya", days=14)
    assert series_a1 != series_b


def test_synthetic_series_has_required_keys() -> None:
    """
    Serideki her bir veri noktasının gerekli anahtarları içerdiğini doğrular.
    """
    series = generate_synthetic_series("Antalya", days=5)
    required_keys = {"day_offset", "temperature_c", "humidity_pct", "rainfall_mm"}

    for point in series:
        assert required_keys.issubset(point.keys())


def test_synthetic_series_value_ranges() -> None:
    """
    Sıcaklık, nem ve yağış değerlerinin mantıklı fiziksel aralıklarda olduğunu doğrular.
    """
    series = generate_synthetic_series("Antalya", days=14)

    for point in series:
        # Sıcaklık 15.0 - 35.0 °C arasında
        assert 15.0 <= point["temperature_c"] <= 35.0

        # Nem %40.0 - %95.0 arasında (pozitif)
        assert 40.0 <= point["humidity_pct"] <= 95.0

        # Yağış negatif olamaz (>= 0.0 mm)
        assert point["rainfall_mm"] >= 0.0

        # Offset eksi gün sayısından başlar 0'a kadar devam eder
        assert -13 <= point["day_offset"] <= 0
