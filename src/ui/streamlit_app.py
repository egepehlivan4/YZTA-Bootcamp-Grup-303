"""
FloraGuard — Streamlit UI (Sprint 3)

Bu modül, FloraGuard sisteminin web arayüzünü oluşturur. Yalnızca
kullanıcı etkileşimlerini alır, FastAPI backend'i ile haberleşir (HTTP)
ve sonuçları görselleştirir. Hiçbir iş mantığı veya model çalıştırma
işlemi içermez (katmanlı mimari).

Geliştirici Notu: Hatalı API isteklerini veya connection error'ları
yakalamak için `_make_api_request` adında DRY prensibine uygun genel bir
fonksiyon eklenmiştir.

Çalıştırma:
    streamlit run src/ui/streamlit_app.py
"""

from __future__ import annotations

import os
from datetime import datetime

import requests
import streamlit as st

# Backend API yapılandırması
API_BASE_URL = os.environ.get("FLORAGUARD_API_URL", "http://localhost:8000")

# Sayfa yapılandırması
st.set_page_config(
    page_title="FloraGuard | Yapay Zeka Destekli Tarım",
    page_icon="🌱",
    layout="centered"
)


# ---------------------------------------------------------------------------
# Yardımcı Fonksiyonlar & Oturum Durumu Yönetimi (Session State)
# ---------------------------------------------------------------------------

def _init_session_state() -> None:
    """Oturum değişkenlerini varsayılan değerlerle başlatır."""
    if "access_token" not in st.session_state:
        st.session_state["access_token"] = None
    if "username" not in st.session_state:
        st.session_state["username"] = None
    if "role" not in st.session_state:
        st.session_state["role"] = None


def _auth_headers() -> dict[str, str]:
    """Geçerli token'ı içeren yetkilendirme başlığını (header) döner."""
    return {"Authorization": f"Bearer {st.session_state['access_token']}"}


def _make_api_request(
    method: str,
    endpoint: str,
    **kwargs: Any
) -> requests.Response | None:
    """
    Tüm API isteklerini tek merkezden yöneten DRY (Don't Repeat Yourself) fonksiyonu.
    Bağlantı hatalarını yakalar ve Streamlit arayüzünde hata gösterir.

    Args:
        method: HTTP metodu (GET, POST vs.)
        endpoint: API_BASE_URL sonrasına eklenecek yol (ör: /predict)
        kwargs: requests kütüphanesine iletilecek argümanlar (data, headers, files vb.)

    Returns:
        Başarılıysa Response objesi, bağlantı koptuysa None.
    """
    url = f"{API_BASE_URL}{endpoint}"
    if 'timeout' not in kwargs:
        kwargs['timeout'] = 15  # Varsayılan zaman aşımı süresi

    try:
        response = requests.request(method, url, **kwargs)
        return response
    except requests.ConnectionError:
        st.error(
            f"🚫 Backend sunucusuna ulaşılamadı ({url}). "
            "Uygulama lokalde ise uvicorn'un çalıştığından emin olun."
        )
        return None
    except requests.Timeout:
        st.error("⏳ API isteği zaman aşımına uğradı. Model veya ajan çok yavaş yanıt veriyor olabilir.")
        return None


def _login(username: str, password: str) -> bool:
    """Kullanıcı kimlik doğrulamasını yapar ve JWT token'ı session'a yazar."""
    # API endpoints prefixed with /api per Sprint 3 backend refactor
    response = _make_api_request(
        "POST",
        "/api/auth/token",
        data={"username": username, "password": password}
    )

    if response is None:
        return False

    if response.status_code != 200:
        st.error("❌ Kullanıcı adı veya şifre hatalı.")
        return False

    payload = response.json()
    st.session_state["access_token"] = payload["access_token"]
    st.session_state["username"] = username
    st.session_state["role"] = payload["role"]
    return True


def _logout() -> None:
    """Kullanıcının oturum verilerini temizler."""
    for key in ("access_token", "username", "role"):
        st.session_state[key] = None


# ---------------------------------------------------------------------------
# Arayüz - Giriş Ekranı
# ---------------------------------------------------------------------------

_init_session_state()

st.title("🌱 FloraGuard")
st.caption("Bitkiniz önümüzdeki 5 gün içinde hastalanacak mı? Önleyici Karar Destek Sistemi.")

# Kullanıcı giriş yapmamışsa login formunu göster ve uygulamayı durdur
if not st.session_state["access_token"]:
    st.divider()
    st.subheader("🔐 Giriş Yap")
    st.info(
        "Demo hesaplar:\n"
        "* **Çiftçi:** `ciftci1` / `ciftci123`\n"
        "* **Danışman:** `danisman1` / `danisman123`\n"
        "* **Admin:** `admin1` / `admin123`"
    )
    with st.form("login_form"):
        username = st.text_input("Kullanıcı adı")
        password = st.text_input("Şifre", type="password")
        submitted = st.form_submit_button("Giriş Yap", type="primary", use_container_width=True)

    if submitted:
        if _login(username, password):
            st.rerun()
    st.stop()


# ---------------------------------------------------------------------------
# Arayüz - Üst Bilgi Çubuğu (Giriş Yapılmış Durum)
# ---------------------------------------------------------------------------

col_user, col_logout = st.columns([4, 1])
col_user.success(f"Hoş geldiniz, **{st.session_state['username']}** (Rol: {st.session_state['role']})")

if col_logout.button("Çıkış", use_container_width=True):
    _logout()
    st.rerun()

st.divider()

# ---------------------------------------------------------------------------
# Arayüz - Yeni Analiz Formu
# ---------------------------------------------------------------------------

st.subheader("📸 Yeni Bitki Analizi")

# Çiftçi rolündeki kullanıcı kendi ID'sini sabit görür, diğerleri girebilir.
default_farmer_id = st.session_state["username"] if st.session_state["role"] == "farmer" else ""
farmer_id = st.text_input("Çiftçi ID", value=default_farmer_id, placeholder="ör. ciftci1")
location = st.text_input("Konum (şehir/ilçe)", placeholder="ör. Antalya")
crop_type = st.selectbox("Ürün Tipi", ["domates", "biber", "salatalik", "patates", "bugday"])

uploaded_file = st.file_uploader(
    "Yaprak fotoğrafı yükleyin (JPEG/PNG Formatı)",
    type=["jpg", "jpeg", "png"],
    help="Hastalığı net olarak gösteren, iyi aydınlatılmış tek bir yaprak fotoğrafı tercih edilir.",
)

if uploaded_file is not None:
    st.image(uploaded_file, caption="Yüklenen Analiz Görseli", use_container_width=True)

    analyze_disabled = not farmer_id or not location

    if st.button("🔍 Yapay Zeka ile Analiz Et", type="primary", use_container_width=True, disabled=analyze_disabled):
        with st.spinner("Orkestratör Ajan çalışıyor: CNN sınıflandırması, LSTM risk tahmini ve geçmiş hafıza taranıyor..."):

            response = _make_api_request(
                "POST",
                "/api/predict",
                headers=_auth_headers(),
                files={"image": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)},
                data={"farmer_id": farmer_id, "location": location, "crop_type": crop_type},
                timeout=120, # Ajan yanıtı için uzun süre tanıyoruz
            )

        if response is not None:
            if response.status_code == 200:
                result = response.json()
                st.divider()
                st.subheader("📊 Analiz Sonuçları")

                # Skor Kartları (Metric)
                col1, col2 = st.columns(2)
                col1.metric("5 Günlük Hastalık Riski", f"%{result['disease_probability'] * 100:.0f}")
                col2.metric("Tahmini Verim Kaybı", f"%{result['estimated_yield_loss_pct']:.1f}")

                # Model ve Ajan Çıktıları
                st.info(f"**Görüntü Modeli (CNN) Tespiti:** {result['cnn_top_class']}")
                st.text_area("🤖 Orkestratör Ajanın Karar Destek Tavsiyesi", value=result["advice"], disabled=True, height=150)
            else:
                st.error(f"Analiz başarısız oldu (Hata Kodu: {response.status_code}). Detay: {response.text}")

st.divider()

# ---------------------------------------------------------------------------
# Arayüz - Geçmiş Kayıtlar
# ---------------------------------------------------------------------------

st.subheader("📜 Çiftçi Hafızası (Geçmiş Kayıtlar)")
history_farmer_id = st.text_input("Geçmişini görüntülemek istediğiniz Çiftçi ID", value=default_farmer_id, key="history_input")

if st.button("Geçmişi Getir"):
    response = _make_api_request(
        "GET",
        f"/api/history/{history_farmer_id}",
        headers=_auth_headers()
    )

    if response is not None:
        if response.status_code == 200:
            records = response.json()
            if not records:
                st.info("Bu çiftçi için sistemde henüz hafıza/geçmiş kaydı bulunmuyor.")
            else:
                for record in records:
                    ts = datetime.fromisoformat(record["timestamp"]).strftime("%Y-%m-%d %H:%M")
                    with st.expander(f"{ts} — Risk: %{record['disease_probability'] * 100:.0f} | Ürün: {record['crop_type']}"):
                        st.write(f"**Konum:** {record['location']}")
                        st.write(f"**Tahmini verim kaybı:** %{record['estimated_yield_loss_pct']:.1f}")
                        if record.get("advice"):
                            st.write(f"**Önceki Tavsiye:** {record['advice']}")
        else:
            st.error(f"Geçmiş veriler alınamadı (Hata Kodu: {response.status_code}). Detay: {response.text}")

st.divider()
st.caption("Yapay Zeka ve Teknoloji Akademisi Bootcamp 2026 — Sprint 3: Canlıya Alma ve Optimizasyon")