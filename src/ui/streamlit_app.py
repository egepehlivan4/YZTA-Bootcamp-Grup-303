"""
FloraGuard — Streamlit UI (Sprint 3)

Bu modül, FloraGuard sisteminin web arayüzünü oluşturur. Yalnızca
kullanıcı etkileşimlerini alır, FastAPI backend'i ile haberleşir
(`src/ui/api_client.py` üzerinden) ve sonuçları görselleştirir
(`src/ui/styles.py`). Hiçbir iş mantığı veya model çalıştırma işlemi
içermez (katmanlı mimari).

Çalıştırma:
    streamlit run src/ui/streamlit_app.py
"""

from __future__ import annotations

from datetime import datetime

import pandas as pd
import streamlit as st

from src.ui import api_client
from src.ui.styles import inject_global_styles, risk_badge_html, risk_level

MAX_IMAGE_SIZE_MB = 10
CROP_OPTIONS = ["domates", "biber", "salatalik", "patates", "bugday"]

st.set_page_config(
    page_title="FloraGuard | Yapay Zeka Destekli Tarım",
    page_icon="🌱",
    layout="wide",
)


# ---------------------------------------------------------------------------
# Oturum Durumu Yönetimi (Session State)
# ---------------------------------------------------------------------------

def _init_session_state() -> None:
    st.session_state.setdefault("access_token", None)
    st.session_state.setdefault("username", None)
    st.session_state.setdefault("role", None)


def _is_authenticated() -> bool:
    return st.session_state["access_token"] is not None


def _login(username: str, password: str) -> bool:
    result = api_client.login(username, password)
    if not result.ok:
        st.error(f"❌ Giriş başarısız: {result.message}")
        return False

    st.session_state["access_token"] = result.data["access_token"]
    st.session_state["username"] = username
    st.session_state["role"] = result.data["role"]
    return True


def _logout() -> None:
    for key in ("access_token", "username", "role"):
        st.session_state[key] = None


# ---------------------------------------------------------------------------
# Arayüz - Ortak Bileşenler
# ---------------------------------------------------------------------------

def _render_hero() -> None:
    st.markdown(
        """
        <div class="fg-hero">
            <h1>🌱 FloraGuard</h1>
            <p>Bitkiniz önümüzdeki 5 gün içinde hastalanacak mı? Yapay zeka destekli önleyici karar destek sistemi.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_login_screen() -> None:
    _, center, _ = st.columns([1, 1.4, 1])
    with center:
        st.markdown('<div class="fg-card">', unsafe_allow_html=True)
        st.subheader("🔐 Giriş Yap")
        st.info(
            "**Demo hesaplar**\n\n"
            "* Çiftçi: `ciftci1` / `ciftci123`\n"
            "* Danışman: `danisman1` / `danisman123`\n"
            "* Admin: `admin1` / `admin123`"
        )
        with st.form("login_form"):
            username = st.text_input("Kullanıcı adı")
            password = st.text_input("Şifre", type="password")
            submitted = st.form_submit_button("Giriş Yap", type="primary", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    if submitted:
        if not username or not password:
            st.warning("Kullanıcı adı ve şifre boş bırakılamaz.")
        elif _login(username, password):
            st.rerun()


def _render_sidebar() -> None:
    with st.sidebar:
        st.markdown("### 🌱 FloraGuard")
        st.success(f"**{st.session_state['username']}**\n\nRol: `{st.session_state['role']}`")
        if st.button("Çıkış Yap", use_container_width=True):
            _logout()
            st.rerun()
        st.divider()
        st.caption("Yapay Zeka ve Teknoloji Akademisi Bootcamp 2026")
        st.caption("Sprint 3 — Canlıya Alma ve Optimizasyon")


# ---------------------------------------------------------------------------
# Arayüz - Yeni Analiz Sekmesi
# ---------------------------------------------------------------------------

def _default_farmer_id() -> str:
    return st.session_state["username"] if st.session_state["role"] == "farmer" else ""


def _render_result(result: dict) -> None:
    label, _ = risk_level(result["disease_probability"])
    st.markdown('<div class="fg-card">', unsafe_allow_html=True)
    st.markdown(f"#### 📊 Analiz Sonuçları &nbsp; {risk_badge_html(result['disease_probability'])}", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    col1.metric("5 Günlük Hastalık Riski", f"%{result['disease_probability'] * 100:.0f}", help=label)
    col2.metric("Tahmini Verim Kaybı", f"%{result['estimated_yield_loss_pct']:.1f}")
    col3.metric("CNN Tespiti", result["cnn_top_class"])

    st.progress(min(max(result["disease_probability"], 0.0), 1.0))

    st.markdown("**🤖 Orkestratör Ajanın Karar Destek Tavsiyesi**")
    st.markdown(f'<div class="fg-advice">{result["advice"]}</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def _render_analysis_tab() -> None:
    left, right = st.columns([1.1, 0.9])

    with left:
        st.markdown('<div class="fg-card">', unsafe_allow_html=True)
        st.markdown("#### 📝 Çiftlik Bilgileri")
        default_farmer_id = _default_farmer_id()
        farmer_id = st.text_input("Çiftçi ID", value=default_farmer_id, placeholder="ör. ciftci1")
        location = st.text_input("Konum (şehir/ilçe)", placeholder="ör. Antalya")
        crop_type = st.selectbox("Ürün Tipi", CROP_OPTIONS)
        uploaded_file = st.file_uploader(
            "Yaprak fotoğrafı yükleyin (JPEG/PNG, maks. 10 MB)",
            type=["jpg", "jpeg", "png"],
            help="Hastalığı net olarak gösteren, iyi aydınlatılmış tek bir yaprak fotoğrafı tercih edilir.",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="fg-card">', unsafe_allow_html=True)
        st.markdown("#### 🖼️ Önizleme")
        if uploaded_file is not None:
            st.image(uploaded_file, use_container_width=True)
        else:
            st.caption("Analiz için soldan bir yaprak fotoğrafı yükleyin.")
        st.markdown("</div>", unsafe_allow_html=True)

    if uploaded_file is None:
        return

    size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
    if size_mb > MAX_IMAGE_SIZE_MB:
        st.error(f"🚫 Görsel çok büyük ({size_mb:.1f} MB). Lütfen {MAX_IMAGE_SIZE_MB} MB altında bir dosya yükleyin.")
        return

    missing_fields = not farmer_id or not location
    if missing_fields:
        st.warning("Analizi başlatmak için Çiftçi ID ve Konum alanlarını doldurun.")

    if st.button("🔍 Yapay Zeka ile Analiz Et", type="primary", use_container_width=True, disabled=missing_fields):
        with st.spinner("Orkestratör Ajan çalışıyor: CNN sınıflandırması, LSTM risk tahmini ve geçmiş hafıza taranıyor..."):
            result = api_client.predict(
                st.session_state["access_token"],
                farmer_id=farmer_id,
                location=location,
                crop_type=crop_type,
                image_name=uploaded_file.name,
                image_bytes=uploaded_file.getvalue(),
                image_type=uploaded_file.type,
            )

        if not result.ok:
            st.error(f"Analiz başarısız oldu: {result.message}")
        else:
            _render_result(result.data)


# ---------------------------------------------------------------------------
# Arayüz - Geçmiş Kayıtlar Sekmesi
# ---------------------------------------------------------------------------

def _render_history_trend(records: list[dict]) -> None:
    if len(records) < 2:
        return
    chart_df = pd.DataFrame(
        {
            "Tarih": [datetime.fromisoformat(r["timestamp"]) for r in reversed(records)],
            "Hastalık Riski (%)": [r["disease_probability"] * 100 for r in reversed(records)],
        }
    ).set_index("Tarih")
    st.line_chart(chart_df, height=220)


def _render_history_tab() -> None:
    st.markdown('<div class="fg-card">', unsafe_allow_html=True)
    st.markdown("#### 📜 Çiftçi Hafızası (Geçmiş Kayıtlar)")
    col_id, col_limit, col_btn = st.columns([2, 1, 1])
    farmer_id = col_id.text_input(
        "Geçmişini görüntülemek istediğiniz Çiftçi ID", value=_default_farmer_id(), key="history_input"
    )
    limit = col_limit.slider("Kayıt sayısı", min_value=5, max_value=50, value=20, step=5)
    col_btn.markdown("<div style='height: 1.8rem;'></div>", unsafe_allow_html=True)
    fetch = col_btn.button("Geçmişi Getir", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if not fetch:
        return

    if not farmer_id:
        st.warning("Lütfen bir Çiftçi ID girin.")
        return

    result = api_client.get_history(st.session_state["access_token"], farmer_id, limit=limit)
    if not result.ok:
        st.error(f"Geçmiş veriler alınamadı: {result.message}")
        return

    records = result.data
    if not records:
        st.info("Bu çiftçi için sistemde henüz hafıza/geçmiş kaydı bulunmuyor.")
        return

    _render_history_trend(records)

    for record in records:
        ts = datetime.fromisoformat(record["timestamp"]).strftime("%Y-%m-%d %H:%M")
        badge = risk_badge_html(record["disease_probability"])
        with st.expander(f"{ts} — {record['crop_type']} — Risk: %{record['disease_probability'] * 100:.0f}"):
            st.markdown(badge, unsafe_allow_html=True)
            st.write(f"**Konum:** {record['location']}")
            st.write(f"**Tahmini verim kaybı:** %{record['estimated_yield_loss_pct']:.1f}")
            if record.get("advice"):
                st.write(f"**Önceki Tavsiye:** {record['advice']}")


# ---------------------------------------------------------------------------
# Giriş Noktası
# ---------------------------------------------------------------------------

def main() -> None:
    inject_global_styles()
    _init_session_state()
    _render_hero()

    if not _is_authenticated():
        _render_login_screen()
        return

    _render_sidebar()

    analysis_tab, history_tab = st.tabs(["📸 Yeni Analiz", "📜 Geçmiş Kayıtlar"])
    with analysis_tab:
        _render_analysis_tab()
    with history_tab:
        _render_history_tab()


main()
