# Sprint 3 Review & Retrospective

**Tarih:** 1 Ağustos 2026  
**Katılımcılar:** Ege Pehlivan (SM), Murad Arıcan (PO), Ahmet Muhammet Gayıp (Dev 1), Arif Bayındır (Dev 2), Ecem Nur Özen (Dev 3)

---

## Sprint 3 Review

**Sprint Hedefi:** Ürünü canlıya almak, temiz kod/mimari son halini vermek ve tüm dokümantasyonu tamamlamak.  
**Durum:** Tamamlandı.

**Tamamlanan Story'ler:**
* LLM provider (Groq/ChatGroq) tutarsızlığı giderildi, `config.py` ve `orchestrator.py` tam uyumlu hale getirildi.
* Kod tabanı temiz kod (Clean Code) prensiplerine göre refactor edildi; çift prefix bug'ı düzeltildi ve modern Python type hint'leri eklendi.
* 4 yeni test dosyası eklendi, toplam otomatik test sayısı 13'ten 25+'e çıkarılarak kritik akışların test kapsama oranı artırıldı.
* Dockerfile içerisindeki hassas veri kopyalama (.env) güvenlik açığı giderildi, multi-stage yapılı optimize build ve health check mekanizması eklendi.
* Canlı ortam yapılandırması için `.env.example` ve `render.yaml` dosyaları oluşturuldu.
* README belgesi mimari, kurulum, API referansı, test adımları ve deployment kılavuzunu içerecek şekilde tüm bölümleriyle tamamlandı.
* 3 dakikalık proje tanıtım videosu çekildi ve final teslim formu eksiksiz dolduruldu.

**Demo Notları:**
Sistem Render cloud platformu üzerinde canlıya alındı. Canlı ortam API servisinin `/health` endpoint'inin başarılı HTTP 200 yanıtı verdiği ve tüm alt bileşenlerin (CNN, LSTM, Regresyon, Orchestrator Agent) çalışır durumda olduğu doğrulandı. Streamlit arayüzü ve backend servisleri canlı ortamda başarıyla test edildi.

---

## Sprint 3 Retrospective

| İyi Gitti | Zorlandık | Deneyeceğiz |
| :--- | :--- | :--- |
| Planda belirlenen LLM provider uyumsuzluğu (Groq vs ChatGroq) erken tespit edilip hızla çözüldü. | Render free tier sunucusunun 512MB RAM limiti, PyTorch ve LLM kütüphanelerinin bellek tüketimi nedeniyle sınırda kaldı. | Gelecek projelerde CI/CD pipeline'ı (GitHub Actions) Sprint 1'den itibaren kurulacak. |
| Docker container simülasyonu Sprint 2 aksiyon maddesine uygun şekilde gerçekleştirildi ve canlıya alım sorunsuz tamamlandı. | Streamlit frontend ile FastAPI backend servislerinin bağımsız çalışabilmesi için ayrı deploy süreçleri yönetilmesi gerekti. | Model ağırlıkları ve büyük veri dosyaları için Git LFS veya S3 gibi bir artifact store kullanılacak. |
| Test coverage artırımı (25+ test senaryosu) kritik tahmin ve orkestrasyon akışlarındaki güveni ve kod kalitesini belirgin şekilde artırdı. | Kısıtlı zaman diliminde video çekimi ve final teslim dokümantasyonunun eşzamanlı yürütülmesi ekip üzerinde yoğunluk yarattı. | Modellerin bellek ayak izini düşürmek için ONNX runtime veya model quantization yöntemleri değerlendirilecek. |

**Aksiyon Maddesi / Kapanış Notu:**
FloraGuard projesinin Sprint 3 hedefleri başarıyla tamamlanmış, canlı ortam kurulumu (deployment), kod optimizasyonları ve tüm teslimat dokümantasyonu eksiksiz olarak finalize edilerek proje teslim aşamasına getirilmiştir.
