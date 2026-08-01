# 1. Hafif ve güvenli bir Python tabanı seçiyoruz
FROM python:3.10-slim

# 2. Çalışma dizinini belirliyoruz
WORKDIR /app

# 3. Sistem bağımlılıklarını güncelliyoruz (Derleme hatalarını önlemek için)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 4. Önce sadece gereksinimleri kopyalıyoruz (Docker Cache Optimizasyonu)
COPY requirements.txt .

# 5. Kritik Optimizasyon: Render (veya ücretsiz bulut) sunucularında GPU yoktur.
# PyTorch'un varsayılan kurulumu CUDA ile gelir ve imajı 2-3 GB şişirir.
# Sadece CPU versiyonunu indirerek imaj boyutunu ve RAM tüketimini minimize ediyoruz.
RUN pip install --no-cache-dir -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu

# 6. Projenin kaynak kodlarını konteynere kopyalıyoruz
# NOT: .env dosyası KOPYALANMAZ — ortam değişkenleri Render dashboard'dan verilmelidir.
COPY src/ src/
COPY main.py main.py
COPY app.py app.py
COPY data/ data/
COPY artifacts/ artifacts/

# 6b. Model ağırlıkları (.pt/.joblib) bilinçli olarak repoya commit edilmiyor
# (bkz. .gitignore) — bu yüzden imaj build edilirken sıfırdan eğitilirler.
# Böylece canlıdaki model, yereldeki gibi GERÇEKTEN eğitilmiş olur (rastgele
# ağırlık/heuristic fallback'e düşmez).
RUN python -m src.models.train_cnn \
    && python -m src.models.train_lstm \
    && python -m src.models.train_regression

# 7. FastAPI'nin çalışacağı portu dışarı açıyoruz
EXPOSE 8000

# 8. Health check — Render ve container orkestrasyonu için kritik
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# 9. Render'ın atayacağı dinamik portu dinleyecek şekilde Uvicorn'u başlatıyoruz
CMD ["sh", "-c", "uvicorn src.api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]