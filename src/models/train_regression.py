"""
FloraGuard — Regresyon Modeli Eğitim Scripti (Sprint 3)

Bu modül, Orkestratör Ajan'ın karar destek sürecinde kullandığı verim kaybı
(YieldLossRegressor) modelini eğitir ve joblib artifact'ı olarak dışa aktarır.

Not: Şu an gerçek saha verisi bulunmadığından izole bir sentetik veri üreteci
kullanılmaktadır. Gerçek veri sağlandığında, pipeline yapısı bozulmadan sadece
veri okuma fonksiyonu değiştirilerek üretim ortamına uyarlanabilir.

Çalıştırma:
    python -m src.models.train_regression
"""

from __future__ import annotations

import logging
import sys

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from src.config import get_settings
from src.models.regression import KNOWN_CROPS

# Loglama konfigürasyonu
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Sabitler (Magic Numbers)
RANDOM_SEED = 42
DEFAULT_N_SAMPLES = 4000


def _make_synthetic_dataset(n_samples: int = DEFAULT_N_SAMPLES, seed: int = RANDOM_SEED) -> pd.DataFrame:
    """
    Geliştirme aşaması için sentetik verim kaybı (yield loss) veri seti üretir.

    TODO: Gerçek saha verisi (CSV veya Veritabanı) entegrasyonu yapılacağı zaman
    bu fonksiyon `pd.read_csv(...)` çağrısına dönüştürülmelidir.

    Args:
        n_samples (int): Üretilecek sentetik veri satırı sayısı.
        seed (int): Rastgelelik kontrolü için seed değeri.

    Returns:
        pd.DataFrame: 'risk_score', 'crop_type' ve 'yield_loss_pct' sütunlarını içeren veri seti.
    """
    logger.info(f"Sentetik veri seti üretiliyor (Örnek Sayısı: {n_samples})...")
    rng = np.random.default_rng(seed)

    # Ürünlerin hastalığa karşı finansal kayıp hassasiyeti
    crop_sensitivity = {
        "domates": 1.0,
        "biber": 0.9,
        "salatalik": 1.1,
        "patates": 0.8,
        "bugday": 0.6
    }

    # Sentetik özellikleri üret (0-1 arası risk skoru, rastgele ürün tipi)
    risk_score = rng.uniform(0, 1, n_samples)
    crop_type = rng.choice(KNOWN_CROPS, n_samples)
    sensitivity = np.array([crop_sensitivity[c] for c in crop_type])

    # Gürültü ekleyerek gerçekçi varyans yarat
    noise = rng.normal(0, 4, n_samples)

    # Temel formül: (Risk Skoru ^ 1.5) * 100 * Ürün Hassasiyeti + Gürültü
    yield_loss_pct = np.clip((risk_score ** 1.5) * 100 * sensitivity + noise, 0, 100)

    return pd.DataFrame({
        "risk_score": risk_score,
        "crop_type": crop_type,
        "yield_loss_pct": yield_loss_pct,
    })


def build_pipeline() -> Pipeline:
    """
    Kategorik verileri (crop_type) işleyen ve Gradient Boosting Regressor
    kullanan makine öğrenmesi pipeline'ını oluşturur.

    Returns:
        Pipeline: Scikit-learn işlem hattı (preprocessor + model).
    """
    preprocessor = ColumnTransformer(
        transformers=[
            ("crop_ohe", OneHotEncoder(handle_unknown="ignore"), ["crop_type"])
        ],
        remainder="passthrough",
    )

    return Pipeline(steps=[
        ("preprocess", preprocessor),
        ("regressor", GradientBoostingRegressor(
            n_estimators=150,
            max_depth=3,
            random_state=RANDOM_SEED
        )),
    ])


def main() -> None:
    """
    Eğitim senaryosunu uçtan uca yönetir:
    1. Veriyi üretir/yükler
    2. Eğitim/Test setlerine böler
    3. Pipeline'ı eğitir ve test metriklerini loglar
    4. Eğitilmiş modeli (artifact) diske kaydeder.
    """
    settings = get_settings()

    try:
        # 1. Veri Hazırlığı
        df = _make_synthetic_dataset()
        X = df[["risk_score", "crop_type"]]
        y = df["yield_loss_pct"]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=RANDOM_SEED
        )

        # 2. Model Eğitimi
        logger.info("Regresyon modeli pipeline eğitimi başlıyor...")
        pipeline = build_pipeline()
        pipeline.fit(X_train, y_train)

        # 3. Model Değerlendirmesi
        predictions = pipeline.predict(X_test)
        mae = mean_absolute_error(y_test, predictions)
        logger.info(f"Test MAE (Ortalama Mutlak Hata): %{mae:.2f} verim kaybı sapması")

        # 4. Modelin Kaydedilmesi
        settings.regression_artifact_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(pipeline, settings.regression_artifact_path)
        logger.info(f"✅ Model başarıyla diske kaydedildi: {settings.regression_artifact_path}")

    except Exception as e:
        logger.error(f"❌ Model eğitim sürecinde kritik hata: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()