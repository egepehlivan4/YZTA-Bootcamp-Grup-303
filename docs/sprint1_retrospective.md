# Sprint 1 - Review & Retrospective

**Tarih:** 5 Temmuz 2026
**Katılım:** Ege Pehlivan (Asenkron iletişimde kopukluklar yaşandığı için notlar SM tarafından derlenmiştir.)

---

## Sprint 1 Review

**Sprint Hedefi:** Mimari iskelet + model prototipleri + proje yönetim altyapısı.
**Durum:** Tamamlandı.

**Tamamlanan Story'ler:**
- GitHub repo, branch stratejisi ve README (JS-01, JS-02)
- FastAPI backend iskeleti — sağlık kontrolü, tahmin ve geçmiş endpoint'leri (JS-03)
- Streamlit frontend iskeleti — fotoğraf yükleme ve önizleme ekranı (JS-04)
- CNN ve LSTM prototip mimarileri; dummy veri ile ileri besleme (forward pass) doğrulandı (JS-05)
- Yaprak görüntü veri setinin belirlenmesi ve ön işleme pipeline'ı (JS-06)
- Hava durumu / nem / sıcaklık verisi için kaynak araştırması (JS-07)
- CNN ve LSTM modellerinin gerçek veri/zaman serisiyle ilk (baseline) eğitimleri (JS-08, JS-09)
- Geçmiş hastalık kayıtları için veri şeması (JS-10)
- Sprint Board'un (Jira) tüm ekiple senkronize edilmesi (JS-11)

**Demo Notları:**
- `uvicorn src.main:app` ile API ayağa kalkıyor, `/health` ve `/predict` (stub) yanıt veriyor.
- `streamlit run src/app.py` ile fotoğraf yükleme ekranı çalışıyor; yüklenen görsel önizleniyor.
- `python src/model_prototypes.py` çalıştırıldığında her iki model dummy girdilerle çıktı üretiyor.

---

## Sprint 1 Retrospective

| İyi Gitti | Zorlandık | Deneyeceğiz |
|---|---|---|
| Teknik iskelet (API + UI + model prototipleri) tek seferde, temiz klasör yapısıyla kuruldu. | **Takım iletişimi:** Ekip üyelerinin farklı zaman dilimlerindeki müsaitlikleri asenkron Daily Scrum düzenini zorladı. | Sprint 2 başında zorunlu bir senkron "yeniden başlatma" toplantısı; herkesin uygunluk takvimini paylaşması. |
| Master plan dokümanı önceliklendirmeyi kolaylaştırdı; puan ağırlıklı story seçimi işe yaradı. | **Zaman yönetimi:** İş yükü sprint sonuna yığıldı; story'ler erken bölünmediği için paralelleşemedi. | Story'leri sprint'in ilk 2 gününde kişilere atamak; "2 gün üst üste güncelleme yoksa SM devralır/yeniden atar" kuralı. |
| Tüm teknik altyapının planlanan sürede bitirilip Jira üzerinde başarıyla "Done" statüsüne getirilmesi. | Board (Jira) senkronizasyonu ilk günlerde zaman aldı. | Jira kullanımını günlük rutin hale getirmek; Daily Scrum'ı boardla eşleştirmek. |

**Aksiyon Maddesi (Sprint 2'ye taşınan):** Sprint 2'nin ilk 48 saati içinde tüm ekiple acil bir senkronizasyon toplantısı yapılacak. Projenin veri bilimi hedefleri doğrultusunda iletişim stratejisi yeniden kurgulanacak. Sorumlu: Ege (SM).
