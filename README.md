# 🌱 FloraGuard — Bitki Hastalığı Tahmin Sistemi

> Yapay Zeka ve Teknoloji Akademisi Bootcamp 2026 — Yapay Zeka & Veri Bilimi Kategorisi

---

## Ürün İle İlgili Bilgiler

Takım İsmi: Grup 303

### Takım Elemanları

| İsim | Rol | Teknik Odak |
|---|---|---|
| Ege Pehlivan | Scrum Master / Developer | Backend (FastAPI), mimari, Agent orkestrasyonu |
| Murad Arıcan | Product Owner / Developer | Backlog yönetimi, veri toplama & regresyon modülü |
| Ahmet Muhammet Gayıp | Developer | CNN modeli (görüntü sınıflandırma) |
| Arif Bayındır | Developer | LSTM modeli (zaman serisi) + ensemble |
| Ecem Nur Özen | Developer | Frontend (Streamlit), RBAC, deployment |

### Ürün İsmi

**FloraGuard**

### Ürün Açıklaması

FloraGuard, çiftçilere yalnızca "bitkiniz şu an hasta mı?" sorusunun cevabını değil, **"bitkiniz önümüzdeki 5 gün içinde hangi olasılıkla hastalanacak?"** öngörüsünü sunan, tahmine dayalı (predictive) bir bitki sağlığı karar destek sistemidir. Yaprak fotoğrafını analiz eden bir CNN modeli ile hava durumu, nem ve sıcaklık zaman serilerini işleyen bir LSTM modelini ensemble mimarisinde birleştirir; bir Orkestratör Ajan, çiftçinin geçmiş verilerini hafızasında tutarak kişiselleştirilmiş tavsiyeler üretir ve olası rekolte kaybını finansal olarak öngörür.

### Ürün Özellikleri

- 📸 **Görüntü tabanlı anlık teşhis:** Yaprak fotoğrafından CNN ile hastalık/sağlık sınıflandırması
- 📈 **5 günlük risk tahmini:** Hava durumu, nem ve sıcaklık verilerinden LSTM ile ileriye dönük hastalık olasılığı
- 🧠 **Ensemble zeka:** CNN + LSTM çıktılarının birleştirilmesiyle tek ve güvenilir bir risk skoru
- 🤖 **Orkestratör Ajan + Hafıza:** Çiftçinin geçmiş kayıtlarını hatırlayan, bağlamsal tavsiye üreten AI ajan mimarisi
- 💰 **Verim kaybı öngörüsü:** Regresyon modülüyle hastalığın yaratacağı tahmini rekolte kaybının finansal etkisi
- 🔐 **Rol bazlı erişim (RBAC):** Çiftçi / Danışman / Admin rolleriyle veri güvenliği
- 🌐 **Canlı web arayüzü:** Streamlit tabanlı, sahada telefondan bile kullanılabilir arayüz

### Hedef Kitle

- Küçük ve orta ölçekli tarım işletmeleri (özellikle sera üreticileri)
- Ziraat mühendisleri ve tarım danışmanları
- Tarım kooperatifleri ve üretici birlikleri
- Tarım sigortası ve agri-tech alanında çalışan kurumlar

---

## Teknik Mimari

### Sistem Genel Bakış

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Streamlit Frontend                           │
│            (Giriş, Fotoğraf Yükleme, Sonuç Görüntüleme)           │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ HTTP / REST
┌──────────────────────────────▼──────────────────────────────────────┐
│                     FastAPI Backend (API Gateway)                    │
│    /health  /api/auth/token  /api/predict  /api/history  /api/weather│
│                        │                                            │
│                  JWT + RBAC Middleware                               │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────┐
│                    Orkestratör Ajan (LangGraph)                     │
│              Groq / Llama 3 70B — Tool-Calling ReAct                │
│                                                                     │
│  ┌────────────┐  ┌─────────────┐  ┌───────────┐  ┌──────────────┐  │
│  │ CNN Tool   │  │ LSTM Tool   │  │ Ensemble  │  │ Regresyon    │  │
│  │ (Yaprak)   │  │ (Hava)      │  │ Tool      │  │ Tool         │  │
│  └─────┬──────┘  └──────┬──────┘  └─────┬─────┘  └──────┬───────┘  │
│        │                │               │                │          │
│  ┌─────▼──────┐  ┌──────▼──────┐  ┌─────▼─────┐  ┌──────▼───────┐  │
│  │ LeafCNN    │  │ WeatherLSTM │  │ Ağırlıklı │  │ GBR Pipeline │  │
│  │ (PyTorch)  │  │ (PyTorch)   │  │ Ortalama  │  │ (Scikit-lrn) │  │
│  └────────────┘  └─────────────┘  └───────────┘  └──────────────┘  │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │             Çiftçi Hafızası (SQLite — predictions tablosu)   │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

### Dizin Yapısı (Sprint 3 — v1.0.0)

```
floraguard/
├── src/
│   ├── models/          # CNN, LSTM, Ensemble, Regresyon (Scikit-learn)
│   │   ├── cnn_model.py        # LeafCNN + CNNPredictor (yaprak sınıflandırma)
│   │   ├── lstm_model.py       # WeatherLSTM + LSTMPredictor (zaman serisi)
│   │   ├── ensemble.py         # Ağırlıklı ortalama risk birleştirici
│   │   ├── regression.py       # YieldLossRegressor (verim kaybı tahmini)
│   │   └── train_regression.py # Regresyon eğitim scripti (sentetik veri)
│   ├── agent/           # Hafıza (SQLite), Tool tanımları, LangGraph Orkestratör
│   │   ├── orchestrator.py     # OrchestratorService — ana giriş noktası (facade)
│   │   ├── tools.py            # LangChain StructuredTool sarmalayıcıları
│   │   ├── prompts.py          # Ajan sistem prompt'u ve görev şablonu
│   │   └── memory.py           # FarmerMemory — çiftçi geçmişi (SQLite)
│   ├── security/        # JWT üretimi + Rol Bazlı Erişim Kontrolü (RBAC)
│   │   ├── auth.py             # Token üretim/çözümleme
│   │   ├── rbac.py             # FastAPI dependency'leri (rol kontrolü)
│   │   └── users_db.py         # Kullanıcı deposu (bcrypt + demo seed)
│   ├── api/             # FastAPI route'ları
│   │   ├── main.py             # Uygulama fabrikası + lifespan yönetimi
│   │   ├── dependencies.py     # Dependency injection (app.state erişimi)
│   │   └── routes/
│   │       ├── auth.py         # POST /api/auth/token
│   │       ├── predict.py      # POST /api/predict
│   │       ├── history.py      # GET  /api/history/{farmer_id}
│   │       └── weather.py      # GET  /api/weather/{location}
│   ├── data/            # Paylaşılan şemalar, SQLite bağlantısı, hava verisi
│   │   ├── schemas.py          # Pydantic veri modelleri (API sözleşmesi)
│   │   ├── database.py         # SQLite bağlantı yardımcısı (WAL modu)
│   │   └── weather_source.py   # Sentetik hava serisi üreteci
│   ├── ui/              # Streamlit arayüzü
│   │   └── streamlit_app.py    # Web frontend (login, analiz, geçmiş)
│   └── config.py        # Merkezi konfigürasyon (pydantic-settings)
├── tests/               # Pytest test dosyaları
│   ├── test_ensemble.py
│   ├── test_memory.py
│   ├── test_rbac.py
│   ├── test_regression.py
│   ├── test_api_health.py
│   ├── test_cnn_predictor.py
│   ├── test_lstm_predictor.py
│   ├── test_weather_source.py
│   └── test_smoke.py           # Canlı ortam smoke test
├── data/                # Çalışma zamanı verileri (SQLite DB, yüklenen görseller)
├── artifacts/           # Eğitilmiş model dosyaları (.pt, .joblib)
├── Dockerfile           # Docker container tanımı (Render uyumlu)
├── render.yaml          # Render Blueprint (one-click deploy)
├── requirements.txt     # Python bağımlılıkları
├── .env.example         # Ortam değişkenleri şablonu
└── .gitignore
```

---

## Kurulum

### Ön Gereksinimler

- Python 3.10+
- pip (Python paket yöneticisi)
- Groq API anahtarı ([console.groq.com](https://console.groq.com) adresinden ücretsiz alınabilir)

### Yerel Kurulum

```bash
# 1. Repoyu klonlayın
git clone <repo-url>
cd YZTA-Bootcamp-Grup303

# 2. Sanal ortam oluşturup aktifleştirin
python3 -m venv .venv && source .venv/bin/activate

# 3. Bağımlılıkları yükleyin
pip install -r requirements.txt

# 4. Ortam değişkenlerini ayarlayın
cp .env.example .env
# .env dosyasını düzenleyerek GROQ_API_KEY ve JWT_SECRET_KEY değerlerini doldurun

# 5. (Önerilir) Regresyon modelini eğitin — yoksa heuristic fallback kullanılır
python -m src.models.train_regression

# 6. Backend'i başlatın
uvicorn src.api.main:app --reload

# 7. Frontend'i başlatın (ayrı terminalde)
streamlit run src/ui/streamlit_app.py
```

### Docker ile Kurulum

```bash
# Docker imajını oluşturun
docker build -t floraguard .

# Container'ı çalıştırın (ortam değişkenlerini .env dosyasından okuyarak)
docker run -p 8000:8000 --env-file .env floraguard
```

### Render ile Deploy

1. GitHub reposunu Render'a bağlayın
2. **New Web Service** → **Docker** seçin
3. Environment Variables bölümüne `GROQ_API_KEY` ve diğer değişkenleri ekleyin
4. Deploy butonuna tıklayın

Veya `render.yaml` Blueprint dosyasını kullanarak:
```bash
# Render CLI ile tek komutla deploy
render blueprint apply
```

---

## API Dokümantasyonu

Backend çalışırken interaktif API dokümantasyonuna erişebilirsiniz:
- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Endpoint Özeti

| Metod | Yol | Açıklama | Yetkilendirme |
|---|---|---|---|
| `GET` | `/health` | Sistem sağlık kontrolü | Açık |
| `POST` | `/api/auth/token` | JWT token üretimi (login) | Açık |
| `POST` | `/api/predict` | Uçtan uca bitki analizi (CNN+LSTM+Ensemble+Ajan) | JWT |
| `GET` | `/api/history/{farmer_id}` | Çiftçi geçmiş kayıtları | JWT + RBAC |
| `GET` | `/api/weather/{location}` | Hava durumu zaman serisi (LSTM girdisi) | JWT |

### Demo Giriş Bilgileri (RBAC Test)

| Kullanıcı Adı | Şifre | Rol |
|---|---|---|
| `ciftci1` | `ciftci123` | Çiftçi (farmer) |
| `danisman1` | `danisman123` | Danışman (advisor) |
| `admin1` | `admin123` | Yönetici (admin) |

---

## Ortam Değişkenleri

Tüm ayarlar `.env` dosyasından okunur. Şablon için `.env.example` dosyasına bakınız.

| Değişken | Açıklama | Zorunlu | Varsayılan |
|---|---|---|---|
| `GROQ_API_KEY` | Groq LLM API anahtarı | ✅ | — |
| `JWT_SECRET_KEY` | JWT token imzalama anahtarı | ✅ | `CHANGE_ME_IN_PRODUCTION` |
| `LLM_MODEL` | Kullanılacak LLM modeli | ❌ | `llama3-70b-8192` |
| `LLM_TEMPERATURE` | LLM yaratıcılık parametresi | ❌ | `0.3` |
| `ENSEMBLE_W_CNN` | CNN ensemble ağırlığı | ❌ | `0.55` |
| `ENSEMBLE_W_LSTM` | LSTM ensemble ağırlığı | ❌ | `0.45` |
| `JWT_ALGORITHM` | JWT imzalama algoritması | ❌ | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token geçerlilik süresi (dk) | ❌ | `60` |
| `FLORAGUARD_API_URL` | Frontend → Backend URL | ❌ | `http://localhost:8000` |
| `ENVIRONMENT` | Çalışma ortamı | ❌ | `development` |

---

## Testler

### Testleri Çalıştırma

```bash
# Tüm birim testlerini çalıştır
python -m pytest tests/ -v --tb=short

# Sadece belirli bir modülü test et
python -m pytest tests/test_ensemble.py -v

# Canlı ortam smoke test (deploy sonrası)
FLORAGUARD_LIVE_URL=https://your-app.onrender.com python -m pytest tests/test_smoke.py -v
```

### Test Kapsamı

| Test Dosyası | Kapsam | Test Sayısı |
|---|---|---|
| `test_ensemble.py` | Ağırlıklı ortalama, input doğrulama | 3 |
| `test_memory.py` | Kayıt ekleme/okuma, özet üretimi | 3 |
| `test_rbac.py` | Token roundtrip, rol kontrolü | 4 |
| `test_regression.py` | Heuristic fallback, monotonik kayıp | 3 |
| `test_api_health.py` | Health endpoint, auth akışı | 4 |
| `test_cnn_predictor.py` | CNN başlatma, predict formatı | 3 |
| `test_lstm_predictor.py` | LSTM başlatma, risk aralığı | 3 |
| `test_weather_source.py` | Determinizm, veri formatı | 4 |
| `test_smoke.py` | Canlı ortam uçtan uca akış | 4 |

---

## Sprint Dokümantasyonu

### Sprint 1: Temel ve Prototip
- [Sprint 1 Backlog](sprint1_backlog.md)
- [Sprint 1 Daily Scrum](sprint1_daily_scrum.md)
- [Sprint 1 Retrospective](sprint1_retrospective.md)

### Sprint 2: Entegrasyon ve Zeka
- [Sprint 2 Backlog](sprint2_backlog.md)
- [Sprint 2 Daily Scrum](sprint2_daily_scrum.md)
- [Sprint 2 Retrospective](sprint2_retrospective.md)

### Sprint 3: Canlıya Alma ve Optimizasyon
- [Sprint 3 Backlog](sprint3_backlog.md)
- [Sprint 3 Daily Scrum](sprint3_daily_scrum.md)
- [Sprint 3 Retrospective](sprint3_retrospective.md)

### Product Backlog

Projemizin ana iş listesine (Product Backlog) ve sprint pano ekran görüntülerine yukarıdaki dokümanlardan ulaşabilirsiniz.

---

## Lisans

Bu proje Yapay Zeka ve Teknoloji Akademisi Bootcamp 2026 kapsamında geliştirilmiştir.
