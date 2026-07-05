# Sprint 1 — Daily Scrum Notları (Asenkron)

**Format:** Ekip üyelerinin farklı zaman dilimlerindeki yoğunlukları nedeniyle Daily Scrum toplantıları Slack üzerinden asenkron (yazılı) olarak yürütülmüştür. Aşağıda sprint boyunca alınan 3 ana durum değerlendirme (check-in) kaydı bulunmaktadır.

---

## 📅 Check-in 1: 22 Haziran 2026 (Sprint Başı)

| İsim | Dün Ne Yaptım? | Bugün Ne Yapacağım? | Blocker |
|---|---|---|---|
| **Ege (SM)** | Proje repo'sunu açtım, branch stratejisini belirledim. | FastAPI backend iskeletini (stub) kuracağım. | Yok. |
| **Murad (PO)** | Ürün fikrini ve README taslağını hazırladım. | Uygun yaprak veri setlerini (PlantVillage vb.) araştıracağım. | Yok. |
| **Ahmet** | CNN modelleri üzerine literatür taraması yaptım. | PyTorch ile temel CNN mimarisini (stub) yazacağım. | Yok. |
| **Arif** | Hava durumu APIsine uygun zaman serisi formatlarına baktım. | LSTM prototip sınıfını oluşturacağım. | Yok. |
| **Ecem** | Figma'da basit bir ekran kurguladım. | Streamlit ile fotoğraf yükleme arayüzünü kodlamaya başlayacağım. | Yok. |

---

## 📅 Check-in 2: 28 Haziran 2026 (Sprint Ortası)

| İsim | Dün Ne Yaptım? | Bugün Ne Yapacağım? | Blocker |
|---|---|---|---|
| **Ege (SM)** | `/health` ve `/predict` endpoint'lerini yazdım. | Model iskeletlerinin backend'e entegrasyonu için hazırlık yapacağım. Jira board'u güncelleyeceğim. | Yok. |
| **Murad (PO)** | Veri seti ön işleme pipeline'ını tamamladım. | Hava durumu geçmiş verisi için şema çıkaracağım. | Ahmet'in CNN input boyutu (128x128) kararına ihtiyacım var. |
| **Ahmet** | `LeafCNN` iskeletini yazdım, dummy veriyle test ettim. | Gerçek veri setiyle ilk eğitim (baseline) denemesine başlayacağım. | Yok. (Murad'a boyut bilgisini ilettim). |
| **Arif** | `WeatherLSTM` iskeletini ve ensemble taslağını yazdım. | Zaman serisi verisiyle eğitim ayarlamalarını yapacağım. | Ücretsiz hava durumu API sınırlarına takılıyorum. |
| **Ecem** | Streamlit UI kodlamasını bitirdim. | `app.py` içine sprint 1 stub uyarılarını ve mock metrikleri ekleyeceğim. | Yok. |

---

## 📅 Check-in 3: 3 Temmuz 2026 (Sprint Kapanışa Doğru)

*Not: Bu tarihte asenkron iletişime geç dönüşler olmuş, süreç Scrum Master (Ege) tarafından koordine edilip toparlanmıştır.*

| İsim | Dün Ne Yaptım? | Bugün Ne Yapacağım? | Blocker |
|---|---|---|---|
| **Ege (SM)** | Model prototiplerinin (stub) boyut doğrulamalarını (smoke test) yaptım. | Sprint teslim evraklarını (Backlog, Retro, README) toparlayıp Jira'yı kapatacağım. | Ekip içi iletişimde kopukluk var, baseline eğitimler (JS-08, JS-09) yetişmeyecek gibi. |
| **Murad (PO)** | Geçmiş hastalık kayıtları için şemayı oluşturduk. | (Slack mesajına dönülmedi) | - |
| **Ahmet** | (Slack mesajına dönülmedi) | (SM Notu: CNN baseline Sprint 2'ye devredildi) | İletişim kopukluğu. |
| **Arif** | (Slack mesajına dönülmedi) | (SM Notu: LSTM baseline Sprint 2'ye devredildi) | İletişim kopukluğu. |
| **Ecem** | Frontend iskeletini son haline getirdim, commit attım. | UI tarafında testleri bitireceğim. | Yok. |