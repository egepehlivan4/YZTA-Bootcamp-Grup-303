# Sprint 3: Canlıya Alma, Optimizasyon ve Final Teslim Backlog Raporu

**Sprint Süresi:** 20 Temmuz - 1 Ağustos 2026  
**Sprint Hedefi:** Ürünü canlıya almak, temiz kod/mimari son halini vermek ve tüm dokümantasyonu tamamlamak.

---

## 1. Backlog Listesi ve Görev Dağılımı

| Epic Numarası ve Adı | Story (Görev) | Sorumlu | Tahmini Efor (Story Point) |
| :--- | :--- | :--- | :--- |
| **Epic 9: Kalite ve Optimizasyon** | LLM provider tutarsızlığının düzeltilmesi | Ege Pehlivan (SM) | 3 |
| **Epic 9: Kalite ve Optimizasyon** | Kod tabanının refactor edilmesi - temiz kod prensipleri, katman ayrımı | Ecem Nur Özen (Dev 3) | 5 |
| **Epic 9: Kalite ve Optimizasyon** | Temel test senaryolarının yazılması - kritik akış testleri | Arif Bayındır (Dev 2) | 5 |
| **Epic 10: Deployment** | Dockerfile güvenlik düzeltmeleri ve optimizasyonu | Ege Pehlivan (SM) | 3 |
| **Epic 10: Deployment** | Render platformuna deployment | Ecem Nur Özen (Dev 3) | 5 |
| **Epic 10: Deployment** | Canlı ortamda smoke test | Ahmet Muhammet Gayıp (Dev 1) | 3 |
| **Epic 11: Final Teslim** | README'nin tüm bölümlerinin tamamlanması | Murad Arıcan (PO) | 5 |
| **Epic 11: Final Teslim** | Sprint 3 Review & Retrospective belgelerinin hazırlanması | Murad Arıcan (PO) | 2 |
| **Epic 11: Final Teslim** | 3 dakikalık proje tanıtım videosunun hazırlanması | Tüm Takım | 3 |
| **Epic 11: Final Teslim** | Final teslim formunun doldurulması | Ege Pehlivan (SM) | 1 |

---

## 2. Backlog Dağıtma ve Efor Tahmini Mantığı

Jüri değerlendirme kriterlerine ve ürünün canlıya alım/teslim gereksinimlerine istinaden Sprint 3 iş dağılımımız şu prensiplere göre yapılandırılmıştır:

* **Kalite ve Optimizasyon Odaklılığı:** Sprint 2'de elde edilen uçtan uca çalışan yapının üzerine, kod kalitesini artırma ve teknik borçları temizleme hedefi koyulmuştur. `config.py` ve `orchestrator.py` arasındaki LLM provider tutarsızlığının (Groq/ChatGroq) giderilmesi SM tarafından üstlenilmiş, modern type hint'ler ve katman ayrımını içeren kod refactoring işi Developer 3'e devredilmiştir.
* **Kritik Akış Testleri:** Sistemin karar destek mekanizmasının güvenilirliğini sağlamak adına 4 yeni test modülü (birim ve entegrasyon) yazılması ve test sayısının 25+'e çıkarılması görevi Developer 2'ye atanmıştır.
* **Güvenli ve Optimize Canlıya Alma (Deployment):** Dockerfile içerisindeki `.env` dosyasının imaj içine kopyalanması gibi güvenlik riskleri temizlenmiş ve multi-stage Docker yapısına geçiş yapılmıştır. Render platformu deployment'ı Developer 3 tarafından yürütülmüş, canlı ortam smoke test kontrolleri Developer 1 tarafından gerçekleştirilmiştir.
* **Dokümantasyon ve Final Teslimatlar:** Jüri sunumu ve repo değerlendirmesi için hayati önem taşıyan README belgesinin tamamlanması, mimari şemalar, kurulum ve API belgelerinin yazılması Product Owner sorumluluğuna verilmiştir. 3 dakikalık tanıtım videosu tüm ekibin katılımıyla hazırlanmış, bootcamp teslim formları ve süreç dokümantasyonu SM liderliğinde tamamlanmıştır.
* **Efor Tahmini (Story Points):** Puanlama Fibonacci serisine (1, 2, 3, 5) göre yapılmıştır. Kapsamlı kod refactoring, test suite geliştirme, Render deployment ve README hazırlanması en yüksek eforlu görevler (5 SP) olarak belirlenmiştir. Toplam Sprint 3 eforu 35 Story Point olarak planlanmıştır.
