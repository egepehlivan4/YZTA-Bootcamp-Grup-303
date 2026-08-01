# Sprint 3 — Daily Scrum Notları (Asenkron)

**Format:** Ekip üyelerinin yoğun çalışma ve ders programları nedeniyle Daily Scrum güncellemeleri Slack üzerinden profesyonel bir şekilde asenkron olarak yürütülmüştür.

---

## 📅 Check-in 1: 20 Temmuz 2026 (Sprint Başlangıcı)

| Kişi | Dün Ne Yaptım? | Bugün Ne Yapacağım? | Blocker |
| :--- | :--- | :--- | :--- |
| **Ege (SM)** | `config.py` ve `orchestrator.py` içindeki LLM provider (Groq vs ChatGroq) yapılandırmasını inceledim. | LLM provider tutarsızlığını düzelterek config ile orchestrator modüllerini tam uyumlu hale getireceğim. | Yok |
| **Ecem (Dev 3)** | Sprint 2 sonundaki kod tabanını ve modül bağımlılıklarını gözden geçirdim. | Kod refactoring için temiz kod prensipleri ve katman ayrımı (clean architecture) planını hazırlayacağım. | Yok |
| **Murad (PO)** | Sprint 3 backlog önceliklerini ve teslimat takvimini finalize ettim. | README güncellemeleri ve 3 dakikalık video senaryosu için taslak oluşturacağım. | Yok |

**Scrum Master Notu:** Sprint 3'e canlıya alma ve kalite odaklı net bir planla başlandı. LLM provider tutarsızlığı öncelikli görev olarak ele alınıyor.

---

## 📅 Check-in 2: 22 Temmuz 2026 (Refactoring ve Test)

| Kişi | Dün Ne Yaptım? | Bugün Ne Yapacağım? | Blocker |
| :--- | :--- | :--- | :--- |
| **Ecem (Dev 3)** | Çift prefix bug'ını tespit edip düzelttim, fonksiyon parametrelerine modern type hint'ler ekledim. | Katman ayrımını tamamlayıp kod tabanının modüler yapısını güçlendireceğim. | Yok |
| **Arif (Dev 2)** | Mevcut otomatik test senaryolarını (13 test) analiz ettim. | Kritik akışlar (ensemble, LLM agent, RBAC, API) için 4 yeni test dosyası kodlamaya başlayacağım. | Yok |
| **Ahmet (Dev 1)** | Model tahmin modüllerinin çıktı formatlarını ve JSON şemalarını kontrol ettim. | Refactor edilen kod yapısı ile CNN ve LSTM tahmin akışlarını test edeceğim. | Yok |

**Scrum Master Notu:** Refactoring ve test yazım süreçleri paralel olarak sorunsuz devam ediyor. Kod kalitesi ve test kapsama oranı hedeflenen seviyeye yükseltiliyor.

---

## 📅 Check-in 3: 24 Temmuz 2026 (Docker ve Yapılandırma)

| Kişi | Dün Ne Yaptım? | Bugün Ne Yapacağım? | Blocker |
| :--- | :--- | :--- | :--- |
| **Ege (SM)** | Dockerfile içinde `.env` dosyasının imaja kopyalandığı güvenlik açığını tespit ettim. | Dockerfile'ı temizleyip multi-stage build ve `/health` check mekanizması ekleyeceğim. | Yok |
| **Ecem (Dev 3)** | Refactoring aşamasını bitirdim, tip kontrollerini tamamladım. | Canlı ortam için `.env.example` ve `render.yaml` konfigürasyon dosyalarını oluşturacağım. | Yok |
| **Murad (PO)** | README dokümanı için mimari şema ve API endpoint listesini hazırladım. | README kurulum adımları, bağımlılıklar ve test kılavuzu bölümlerini yazacağım. | Yok |

**Scrum Master Notu:** Dockerfile güvenlik açığı giderildi. Render deployment öncesi çevre değişkenleri yapılandırması tamamlanmak üzere.

---

## 📅 Check-in 4: 28 Temmuz 2026 (Render Deploy ve README)

| Kişi | Dün Ne Yaptım? | Bugün Ne Yapacağım? | Blocker |
| :--- | :--- | :--- | :--- |
| **Ecem (Dev 3)** | `.env.example` ve `render.yaml` hazırlıklarını tamamladım. | FastAPI backend servisini Render platformuna deploy edip canlı ortam denemesi yapacağım. | **Var:** Render free tier 512MB RAM limiti PyTorch + LLM kütüphaneleriyle sınırda kalıyor, bağımlılık optimizasyonu yapılıyor. |
| **Murad (PO)** | README dokümanının genel tanıtım ve mimari bölümlerini tamamladım. | API dokümantasyonu, test kılavuzu ve deployment talimatları bölümlerini kaleme alacağım. | Yok |
| **Ahmet (Dev 1)** | Render staging ortamı çıktılarını ve loglarını takip ettim. | Canlıya alınan ortama ilk isteği gönderip smoke test senaryolarını hazırlayacağım. | Yok |

**Scrum Master Notu:** Render free tier RAM limiti uyarısı üzerine gereksiz paketler requirements'tan çıkarılarak optimize edildi ve deploy tamamlandı.

---

## 📅 Check-in 5: 31 Temmuz 2026 (Finalization)

| Kişi | Dün Ne Yaptım? | Bugün Ne Yapacağım? | Blocker |
| :--- | :--- | :--- | :--- |
| **Ege (SM)** | Dockerfile güvenlik ve optimizasyon düzenlemelerini tamamladım. | Final teslim formunu doldurup tüm Sprint 3 dokümanlarının son kontrollerini yapacağım. | Yok |
| **Murad (PO)** | README'nin tüm bölümlerini bitirdim, Review & Retrospective belgelerini hazırladım. | Proje tanıtım videosunun çekim/kurgu kontrollerini tamamlayıp yayınlayacağım. | Yok |
| **Arif (Dev 2)** | 4 yeni test dosyasını tamamlayarak toplam test sayısını 25+'e çıkardım. | Canlı ortamdaki (Render) `/health` ve tahmin endpoint'lerinde smoke testleri doğrulayacağım. | Yok |

**Scrum Master Notu:** Canlı ortam smoke testleri başarıyla geçti (`/health` 200 OK). Tüm testler yeşil ve dokümantasyon tamamlandı. Proje teslime hazır.
