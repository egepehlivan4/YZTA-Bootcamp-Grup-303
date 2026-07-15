# 🌱 FloraGuard — Bitki Hastalığı Tahmin Sistemi

> Yapay Zeka ve Teknoloji Akademisi Bootcamp 2026 — Yapay Zeka & Veri Bilimi Kategorisi

---

## Ürün İle İlgili Bilgiler

Takım İsmi: Grup 303

### Takım Elemanları

| İsim | Rol | Teknik Odak (Öneri) |
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

### Product Backlog URL

Projemizin ana iş listesine (Product Backlog) ve Sprint 1 güncel pano (Board) ekran görüntülerine aşağıdaki dokümandan ulaşabilirsiniz:

👉 [Sprint 1 Backlog ve Board Durumu](docs/)

---

## Teknik Mimari (Özet)

```
Yaprak Fotoğrafı ──► Orkestratör Ajan ──► CNN + LSTM (paralel) ──► Ensemble
                          │                                          │
                       Hafıza ◄──────────── Tavsiye ◄─── Regresyon (verim kaybı)
```

Detaylı mimari için: [`docs/`](docs/) klasörüne bakınız.

## Kurulum

```bash
git clone <repo-url>
cd floraguard
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env   # ANTHROPIC_API_KEY ve JWT_SECRET_KEY'i doldurun

# (opsiyonel ama önerilir) Regresyon modelini eğit — yoksa heuristic fallback kullanılır
python -m src.models.train_regression

# Backend
uvicorn src.api.main:app --reload

# Frontend (ayrı terminalde)
streamlit run src/ui/streamlit_app.py
```

Demo giriş bilgileri (RBAC test için): `ciftci1/ciftci123` (Çiftçi),
`danisman1/danisman123` (Danışman), `admin1/admin123` (Admin).

### Sprint 2 Mimarisi

```
src/
├── models/    # CNN, LSTM, Ensemble, Regresyon (Scikit-learn)
├── agent/     # Hafıza (SQLite), Tool tanımları, LangGraph Orkestratör Ajan
├── security/  # JWT üretimi + Rol Bazlı Erişim Kontrolü (RBAC)
├── api/       # FastAPI route'ları (auth, predict, history, weather)
├── data/      # Paylaşılan şemalar, SQLite bağlantısı, hava durumu kaynağı
└── ui/        # Streamlit arayüzü
```

## Sprint Dokümantasyonu

- [Sprint 1 Backlog ve Board Durumu](sprint1_backlog.md)
- [Daily Scrum Notları](docs/daily-scrum/)
- [Sprint 1 Retrospective](sprint1_retrospective.md)
