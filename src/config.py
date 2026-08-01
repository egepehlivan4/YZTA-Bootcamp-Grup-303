"""
FloraGuard — Merkezi Konfigürasyon
Tüm katmanlar (models, agent, security, api) ayarlarını buradan okur.
.env dosyasından (varsa) otomatik yüklenir; yoksa makul varsayılanlar kullanılır.
"""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- Genel ---
    app_name: str = "FloraGuard API"
    app_version: str = "1.0.0"
    environment: str = "development"

    # --- Depolama ---
    db_path: Path = BASE_DIR / "data" / "floraguard.db"
    regression_artifact_path: Path = BASE_DIR / "artifacts" / "yield_regressor.joblib"
    upload_tmp_dir: Path = BASE_DIR / "data" / "uploads"

    # --- Model ---
    cnn_num_classes: int = 3
    cnn_class_names: tuple[str, ...] = ("saglikli", "hastalik_a", "hastalik_b")
    cnn_weights_path: Path | None = BASE_DIR / "artifacts" / "leaf_cnn.pt"
    lstm_weights_path: Path | None = BASE_DIR / "artifacts" / "weather_lstm.pt"
    ensemble_w_cnn: float = 0.55
    ensemble_w_lstm: float = 0.45

    # --- LLM / Ajan (Groq Altyapısı) ---
    llm_provider: str = "groq"
    groq_api_key: str | None = None
    llm_model: str = "llama3-70b-8192"
    llm_temperature: float = 0.3
    agent_max_iterations: int = 8

    # --- Güvenlik (JWT / RBAC) ---
    jwt_secret_key: str = "CHANGE_ME_IN_PRODUCTION"  # .env üzerinden override edilmeli
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # --- CORS ---
    cors_allow_origins: tuple[str, ...] = ("*",)


@lru_cache
def get_settings() -> Settings:
    """Ayarları tek sefer okuyup önbelleğe alır (uygulama boyunca tekil kaynak)."""
    settings = Settings()
    settings.db_path.parent.mkdir(parents=True, exist_ok=True)
    settings.regression_artifact_path.parent.mkdir(parents=True, exist_ok=True)
    settings.upload_tmp_dir.mkdir(parents=True, exist_ok=True)
    return settings
