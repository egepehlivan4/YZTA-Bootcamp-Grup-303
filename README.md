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
│            Groq / Llama 3.3 70B — Tool-Calling ReAct                │
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
│   │   ├── train_regression.py # Regresyon eğitim scripti
│   │   ├── train_cnn.py        # CNN baseline eğitim scripti
│   │   └── train_lstm.py       # LSTM baseline eğitim scripti
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
│   ├── ui/              # Streamlit arayüzü (katmanlı: sayfa / ağ / stil ayrımı)
│   │   ├── streamlit_app.py    # Sayfa kompozisyonu (login, analiz, geçmiş sekmeleri)
│   │   ├── api_client.py       # Backend HTTP istemcisi (DRY, hata yönetimi tek noktada)
│   │   └── styles.py           # Özel CSS + risk rozeti yardımcıları
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
├── requirements.txt     # Streamlit Cloud için hafif frontend bağımlılıkları (bkz. not aşağıda)
├── requirements-full.txt # Backend dahil TAM bağımlılık listesi (Docker/Render, yerel tam-yığın geliştirme)
├── .env.example         # Ortam değişkenleri şablonu
└── .gitignore
```

---

## Ensemble Birleştirme Mantığı

CNN (görüntü) ve LSTM (hava durumu) modellerinin çıktıları **ağırlıklı ortalama** ile birleştirilir:

```
risk_score = w_cnn × cnn_diseased_probability + w_lstm × lstm_risk_5d
```

Varsayılan ağırlıklar: CNN %55, LSTM %45 (`.env` üzerinden `ENSEMBLE_W_CNN` / `ENSEMBLE_W_LSTM` ile değiştirilebilir). Nihai risk skoru regresyon modülüne girdi olarak verilir ve tahmini verim kaybı hesaplanır.

---

## LLM Seçimi ve Gerekçesi

Orkestratör Ajan'ın tool-calling (CNN/LSTM/ensemble/regresyon çağırma) ve doğal dilde tavsiye üretme ihtiyacı için **Groq API üzerinden Llama 3.3 70B (`llama-3.3-70b-versatile`)** kullanılıyor. Seçim gerekçeleri:

- **Maliyet:** Groq'un öğrenci/geliştirici katmanı ücretsiz ve bootcamp bütçesine uygun; kapalı kaynak alternatiflere (GPT-4 sınıfı) göre token maliyeti yok.
- **Hız:** Groq'un LPU altyapısı, aynı model boyutunda diğer sağlayıcılara göre gözle görülür şekilde düşük gecikme sunuyor — canlı demo/jüri sunumunda kritik.
- **Tool-calling yeteneği:** 70B parametreli Llama 3.3, ReAct tarzı çok adımlı araç çağırma (CNN → LSTM → ensemble → regresyon → hafıza) senaryolarını güvenilir şekilde destekliyor; daha küçük modellerde (8B sınıfı) araç seçim hataları gözlemlendi.
- **Değiştirilebilirlik:** Model adı `.env` üzerinden `LLM_MODEL` ile merkezi olarak yönetiliyor (`src/config.py`); sağlayıcı Groq'un desteklediği modeller değiştikçe (bkz. [console.groq.com/docs/deprecations](https://console.groq.com/docs/deprecations)) kod değişikliği gerekmeden güncellenebilir.

---

## Model Eğitimi

Artifact dosyaları repoda `.gitignore` ile hariç tutulur; ilk kurulumda aşağıdaki komutlarla üretilmelidir:

```bash
python -m src.models.train_cnn        # artifacts/leaf_cnn.pt
python -m src.models.train_lstm       # artifacts/weather_lstm.pt
python -m src.models.train_regression # artifacts/yield_regressor.joblib
```

### CNN Veri Seti Yaklaşımı ve Doğrulama Sonucu

Gerçek bir yaprak hastalığı veri seti bootcamp'in "hazır veri seti/dışarıdan kod
kullanımı" kısıtına takılabileceğinden, `train_cnn.py` içindeki
`LeafLesionSynthesizer`, her sınıf için **görsel olarak ayrışan** prosedürel
görüntüler üretir (rastgele gürültü değil):

| Sınıf | Görsel imza |
|---|---|
| `saglikli` | Düzgün yeşil doku, damar benzeri hafif parlaklık dalgalanması, leke yok |
| `hastalik_a` | 6-12 küçük, halka desenli (target-spot) sarı-kahverengi leke |
| `hastalik_b` | 2-5 büyük, düzensiz, koyu "sulu görünümlü" yama (mildiyö/geç yanıklık benzeri) |

Model, %80/%20 train/val bölünmesi ve augmentation (flip, rotasyon, renk
sıçraması) ile eğitilir; her epoch sonunda doğrulama doğruluğu loglanır.
Son eğitimde doğrulama doğruluğu **rastgele-şans taban çizgisi olan %33'ten
%100'e** çıkmıştır — modelin gerçekten öğrendiğinin kanıtı. `CNNPredictor`
ayrıca bozuk/geçersiz görüntü dosyalarını (`ValueError` → API'de 422 yanıtı)
ve düşük-güvenli (belirsiz) tahminleri (`is_uncertain` alanı) uç durum
olarak yönetir.

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

# 3. Bağımlılıkları yükleyin (backend + frontend birlikte, yerel tam-yığın geliştirme için)
pip install -r requirements-full.txt
# NOT: Kök requirements.txt yalnızca Streamlit Cloud deploy'u için hafif bir
# frontend listesidir (bkz. "Streamlit Community Cloud'a Deploy" bölümü).

# 4. Ortam değişkenlerini ayarlayın
cp .env.example .env
# .env dosyasını düzenleyerek GROQ_API_KEY ve JWT_SECRET_KEY değerlerini doldurun

# 5. (Önerilir) Model artifact'larını eğitin — yoksa heuristic/rastgele fallback kullanılır
python -m src.models.train_cnn
python -m src.models.train_lstm
python -m src.models.train_regression

# 6. Backend'i başlatın
uvicorn src.api.main:app --reload

# 7. Frontend'i başlatın (ayrı terminalde)
streamlit run src/ui/streamlit_app.py
```

### Docker ile Kurulum

Model ağırlıkları (`.pt`/`.joblib`) bilinçli olarak repoya commit edilmez (bkz.
`.gitignore`); bunun yerine **Docker imajı build edilirken sıfırdan eğitilirler**
(`Dockerfile` içindeki `RUN python -m src.models.train_cnn ...` adımı). Bu, canlıya
alınan modelin de yereldeki gibi gerçekten eğitilmiş olmasını garanti eder — build
süresi bu yüzden ~2-3 dakika sürer.

```bash
# Docker imajını oluşturun (modelleri de eğitir, birkaç dakika sürebilir)
docker build -t floraguard .

# Container'ı çalıştırın (ortam değişkenlerini .env dosyasından okuyarak)
docker run -p 8000:8000 --env-file .env floraguard
```

### Render ile Deploy

1. GitHub reposunu Render'a bağlayın
2. **New Web Service** → **Docker** seçin
3. Environment Variables bölümüne `GROQ_API_KEY` ve diğer değişkenleri ekleyin
4. Deploy butonuna tıklayın — build adımı modelleri otomatik eğitir (yukarıya bakınız)

Veya `render.yaml` Blueprint dosyasını kullanarak:
```bash
# Render CLI ile tek komutla deploy
render blueprint apply
```

### Streamlit Community Cloud'a Deploy (Frontend)

Backend'den (Render) ayrı olarak barındırılır — [share.streamlit.io](https://share.streamlit.io) üzerinden:

1. GitHub hesabınızla giriş yapıp **"Deploy a public app from GitHub"** seçin.
2. **Main file path** alanına mutlaka `src/ui/streamlit_app.py` yazın.
3. **Advanced settings → Secrets** kısmına backend URL'sini TOML formatında ekleyin:
   ```toml
   FLORAGUARD_API_URL = "https://<render-backend-url>"
   ```
4. Deploy edin.

**Önemli:** Streamlit Community Cloud, giriş dosyasının konumundan bağımsız olarak
**her zaman kök dizindeki `requirements.txt`'i** kullanır (alt dizindekini otomatik
algılamaz). Bu yüzden kök `requirements.txt` bilinçli olarak yalnızca frontend'in
ihtiyaç duyduğu 3 paketi içerir; backend'in tam listesi `requirements-full.txt`'tedir
ve yalnızca Docker/Render tarafından kullanılır.

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
| `LLM_MODEL` | Kullanılacak LLM modeli | ❌ | `llama-3.3-70b-versatile` |
| `LLM_TEMPERATURE` | LLM yaratıcılık parametresi | ❌ | `0.3` |
| `ENSEMBLE_W_CNN` | CNN ensemble ağırlığı | ❌ | `0.55` |
| `ENSEMBLE_W_LSTM` | LSTM ensemble ağırlığı | ❌ | `0.45` |
| `JWT_ALGORITHM` | JWT imzalama algoritması | ❌ | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token geçerlilik süresi (dk) | ❌ | `60` |
| `FLORAGUARD_API_URL` | Frontend → Backend URL | ❌ | `http://localhost:8000` |
| `OPENWEATHER_API_KEY` | OpenWeatherMap API anahtarı (opsiyonel) | ❌ | — |
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
| `test_ensemble.py` | Ağırlıklı ortalama, input doğrulama | 4 |
| `test_memory.py` | Kayıt ekleme/okuma, özet üretimi | 3 |
| `test_rbac.py` | Token roundtrip, rol kontrolü | 4 |
| `test_regression.py` | Heuristic fallback, monotonik kayıp | 3 |
| `test_api_health.py` | Health endpoint, auth akışı | 4 |
| `test_config.py` | LLM model/ensemble ağırlık sağlamlığı (regresyon koruması) | 2 |
| `test_cnn_predictor.py` | CNN başlatma, predict formatı, uç durumlar (bozuk/boş/çok küçük görüntü, confidence) | 7 |
| `test_lstm_predictor.py` | LSTM başlatma, risk aralığı | 3 |
| `test_weather_source.py` | Determinizm, veri formatı | 4 |
| `test_weather_route.py` | `/api/weather` auth, şema, determinizm (isim çakışması regresyon koruması) | 3 |
| `test_predict_integration.py` | Predict endpoint, auth, deterministik akış, bozuk görüntü 422, **gerçek ajan tool-calling yolu (mock'lu)** | 5 |
| `test_ui_api_client.py` | Streamlit API istemcisi: login/predict/history başarı ve hata yolları | 7 |
| `test_smoke.py` | Canlı ortam uçtan uca akış | 4 |

**Toplam:** 49 birim testi (+ 4 canlı smoke test, `FLORAGUARD_LIVE_URL` ile)

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
