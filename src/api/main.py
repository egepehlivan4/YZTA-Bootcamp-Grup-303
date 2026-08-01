"""
FloraGuard — FastAPI Entry Point

Bu modül, FloraGuard projesinin HTTP API katmanını başlatır.
Yapay zeka modelleri (CNN, LSTM, Regresyon) ve Orkestratör Ajan (LLM)
gibi bellek/işlemci yoğun nesneler uygulamanın yaşam döngüsü (lifespan)
içerisinde yalnızca bir kez yüklenir ve `app.state` üzerinden paylaşıma açılır.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.agent.memory import FarmerMemory
from src.agent.orchestrator import OrchestratorService
from src.api.routes import auth, history, predict, weather
from src.config import get_settings
from src.models.cnn_model import CNNPredictor
from src.models.lstm_model import LSTMPredictor
from src.models.regression import YieldLossRegressor
from src.security.users_db import init_users_table, seed_demo_users

# Loglama konfigürasyonu
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    FastAPI uygulamasının yaşam döngüsünü yönetir.

    Uygulama başlatıldığında veritabanı bağlantılarını kurar,
    ağır ML modellerini (CNN, LSTM) belleğe yükler ve Orkestratör
    Ajanı ayağa kaldırır. Uygulama kapandığında kaynakları serbest bırakır.

    Args:
        app (FastAPI): Çalışan FastAPI uygulama nesnesi.

    Yields:
        None
    """
    settings = get_settings()
    logger.info(f"FloraGuard API başlatılıyor (Ortam: {settings.environment})...")

    # Veritabanı ve kullanıcı hazırlıkları
    try:
        init_users_table(settings.db_path)
        seed_demo_users(settings.db_path)
        logger.info("Kullanıcı veritabanı başarıyla başlatıldı.")
    except Exception as e:
        logger.error(f"Veritabanı başlatılırken hata oluştu: {e}")
        raise

    # Ağır nesnelerin (modeller, hafıza ve ajan) tek seferlik (Singleton) yüklenmesi
    try:
        memory = FarmerMemory(settings.db_path)
        cnn_predictor = CNNPredictor(
            settings.cnn_num_classes,
            settings.cnn_class_names,
            settings.cnn_weights_path
        )
        lstm_predictor = LSTMPredictor(settings.lstm_weights_path)
        regressor = YieldLossRegressor(settings.regression_artifact_path)

        app.state.memory = memory
        app.state.orchestrator = OrchestratorService(
            settings,
            cnn_predictor,
            lstm_predictor,
            regressor,
            memory
        )
        logger.info("Yapay zeka modelleri ve Orkestratör Ajan belleğe yüklendi.")
    except Exception as e:
        logger.error(f"Modeller veya Ajan yüklenirken kritik hata: {e}")
        raise

    logger.info("FloraGuard API hazır ve istekleri kabul ediyor.")

    yield  # Uygulama bu noktada çalışmaya devam eder

    # Uygulama kapatılırken çalışacak temizlik işlemleri
    logger.info("FloraGuard API kapatılıyor. Kaynaklar serbest bırakılıyor...")


def create_app() -> FastAPI:
    """
    FastAPI uygulamasını oluşturur, middleware ve router'ları bağlar.

    Returns:
        FastAPI: Yapılandırılmış ana uygulama nesnesi.
    """
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        description=(
            "Bitki Hastalığı Tahmin Sistemi — "
            "CNN ve LSTM modellerini kullanan tahmine dayalı karar destek API'si."
        ),
        version=settings.app_version,
        lifespan=lifespan,
    )

    # CORS (Cross-Origin Resource Sharing) ayarları
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.cors_allow_origins],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # API Router'larının dahil edilmesi
    app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
    app.include_router(predict.router, prefix="/api/predict", tags=["Prediction"])
    app.include_router(history.router, prefix="/api/history", tags=["History"])
    app.include_router(weather.router, prefix="/api/weather", tags=["Weather"])

    @app.get("/health", tags=["System Health"])
    def health_check() -> dict[str, Any]:
        """
        Sistemin ayakta olup olmadığını kontrol eden health endpoint'i.
        Deployment (Render/AWS) aşamasındaki uptime kontrolleri için kritik.

        Returns:
            Dict[str, Any]: Sistem durumu ve versiyon bilgisi.
        """
        return {
            "status": "ok",
            "service": "floraguard-api",
            "version": settings.app_version,
            "environment": settings.environment
        }

    return app


# Uvicorn veya Gunicorn tarafından çağrılacak ana uygulama nesnesi
app = create_app()