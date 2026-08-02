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
MODIFIER_ROLES = ("advisor", "admin")

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
            <span class="fg-hero-badge">Yapay Zeka Destekli Karar Destek Sistemi</span>
            <h1>🌱 FloraGuard</h1>
            <p>Bitkiniz önümüzdeki 5 gün içinde hastalanacak mı? CNN + LSTM ensemble'ı,
            Orkestratör Ajan ve çiftçi hafızasıyla önleyici, kişiselleştirilmiş tavsiye üretir.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_login_screen() -> None:
    _, center, _ = st.columns([1, 1.3, 1])
    with center:
        with st.container(border=True):
            st.subheader("🔐 Giriş Yap")
            st.info(
                "**Demo hesaplar**\n\n"
                "* Çiftçi: `ciftci1` / `ciftci123`\n"
                "* Danışman: `danisman1` / `danisman123`\n"
                "* Admin: `admin1` / `admin123`"
            )
            with st.form("login_form"):
                username = st.text_input("Kullanıcı adı", key="login_username")
                password = st.text_input("Şifre", type="password", key="login_password")
                submitted = st.form_submit_button("Giriş Yap", type="primary", use_container_width=True)

    if submitted:
        if not username or not password:
            st.warning("Kullanıcı adı ve şifre boş bırakılamaz.")
        elif _login(username, password):
            st.rerun()


_ROLE_LABELS = {"farmer": "Çiftçi", "advisor": "Danışman", "admin": "Admin"}


def _render_sidebar() -> None:
    with st.sidebar:
        st.markdown("### 🌱 FloraGuard")
        role_label = _ROLE_LABELS.get(st.session_state["role"], st.session_state["role"])
        st.success(f"**{st.session_state['username']}**\n\nRol: `{role_label}`")
        if st.session_state["role"] in MODIFIER_ROLES:
            st.caption("✏️ Çiftçi kayıtlarını düzenleme/silme yetkiniz var." if st.session_state["role"] == "advisor"
                       else "✏️ Tüm kayıtları düzenleme/silme yetkiniz var.")
        if st.button("Çıkış Yap", use_container_width=True, key="logout_button"):
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


def _risk_meter_html(probability: float) -> str:
    pct = min(max(probability, 0.0), 1.0) * 100
    return f"""
    <div style="background: rgba(15,70,54,0.08); border-radius: 999px; height: 10px; overflow: hidden; margin: 0.4rem 0 1rem;">
        <div style="width: {pct:.1f}%; height: 100%;
                    background: linear-gradient(90deg, #16664f, #c8a24a);
                    border-radius: 999px;"></div>
    </div>
    """


def _render_result(result: dict) -> None:
    with st.container(border=True):
        st.markdown(f"#### 📊 Analiz Sonuçları &nbsp; {risk_badge_html(result['disease_probability'])}", unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        col1.metric("5 Günlük Hastalık Riski", f"%{result['disease_probability'] * 100:.0f}")
        col2.metric("Tahmini Verim Kaybı", f"%{result['estimated_yield_loss_pct']:.1f}")
        col3.metric("CNN Tespiti", result["cnn_top_class"])

        st.markdown(_risk_meter_html(result["disease_probability"]), unsafe_allow_html=True)

        st.markdown("**🤖 Orkestratör Ajanın Karar Destek Tavsiyesi**")
        st.markdown(f'<div class="fg-advice">{result["advice"]}</div>', unsafe_allow_html=True)


def _render_analysis_tab() -> None:
    left, right = st.columns([1.1, 0.9])

    with left:
        with st.container(border=True):
            st.markdown("#### 📝 Çiftlik Bilgileri")
            default_farmer_id = _default_farmer_id()
            farmer_id = st.text_input(
                "Çiftçi ID", value=default_farmer_id, placeholder="ör. ciftci1", key="analysis_farmer_id",
            )
            location = st.text_input("Konum (şehir/ilçe)", placeholder="ör. Antalya", key="analysis_location")
            crop_type = st.selectbox("Ürün Tipi", CROP_OPTIONS, key="analysis_crop_type")
            uploaded_file = st.file_uploader(
                "Yaprak fotoğrafı yükleyin (JPEG/PNG, maks. 10 MB)",
                type=["jpg", "jpeg", "png"],
                help="Hastalığı net olarak gösteren, iyi aydınlatılmış tek bir yaprak fotoğrafı tercih edilir.",
                key="analysis_uploader",
            )

    with right:
        with st.container(border=True):
            st.markdown("#### 🖼️ Önizleme")
            if uploaded_file is not None:
                st.image(uploaded_file, use_container_width=True)
            else:
                st.caption("Analiz için soldan bir yaprak fotoğrafı yükleyin.")

    if uploaded_file is None:
        return

    size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
    if size_mb > MAX_IMAGE_SIZE_MB:
        st.error(f"🚫 Görsel çok büyük ({size_mb:.1f} MB). Lütfen {MAX_IMAGE_SIZE_MB} MB altında bir dosya yükleyin.")
        return

    missing_fields = not farmer_id or not location
    if missing_fields:
        st.warning("Analizi başlatmak için Çiftçi ID ve Konum alanlarını doldurun.")

    if st.button(
        "🔍 Yapay Zeka ile Analiz Et", type="primary", use_container_width=True,
        disabled=missing_fields, key="analyze_button",
    ):
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


def _render_record_edit_form(record: dict, token: str) -> None:
    """Danışman/Admin için düzenleme formu — yalnızca insan tarafından
    girilebilir alanlar (crop_type/location/advice) değiştirilebilir."""
    with st.form(f"edit_form_{record['id']}", border=False):
        crop_index = CROP_OPTIONS.index(record["crop_type"]) if record["crop_type"] in CROP_OPTIONS else 0
        new_crop = st.selectbox("Ürün Tipi", CROP_OPTIONS, index=crop_index, key=f"crop_{record['id']}")
        new_location = st.text_input("Konum", value=record["location"], key=f"loc_{record['id']}")
        new_advice = st.text_area("Tavsiye", value=record.get("advice") or "", key=f"advice_{record['id']}")
        save_clicked = st.form_submit_button("💾 Kaydet", type="primary")

    if save_clicked:
        result = api_client.update_history_record(
            token, record["id"], crop_type=new_crop, location=new_location, advice=new_advice,
        )
        if result.ok:
            st.success("Kayıt güncellendi.")
            st.rerun()
        else:
            st.error(f"Güncellenemedi: {result.message}")


def _render_record_delete_control(record: dict, token: str) -> None:
    confirm_key = f"confirm_delete_{record['id']}"
    if st.session_state.get(confirm_key):
        st.warning("Bu kaydı kalıcı olarak silmek istediğinize emin misiniz?")
        yes_col, no_col = st.columns(2)
        if yes_col.button("Evet, sil", key=f"yes_{record['id']}", type="primary", use_container_width=True):
            result = api_client.delete_history_record(token, record["id"])
            st.session_state[confirm_key] = False
            if result.ok:
                st.success("Kayıt silindi.")
                st.rerun()
            else:
                st.error(f"Silinemedi: {result.message}")
        if no_col.button("Vazgeç", key=f"no_{record['id']}", use_container_width=True):
            st.session_state[confirm_key] = False
            st.rerun()
    else:
        if st.button("🗑️ Sil", key=f"del_{record['id']}"):
            st.session_state[confirm_key] = True
            st.rerun()


def _render_history_tab() -> None:
    with st.container(border=True):
        st.markdown("#### 📜 Çiftçi Hafızası (Geçmiş Kayıtlar)")
        col_id, col_limit, col_btn = st.columns([2, 1, 1], vertical_alignment="bottom")
        farmer_id = col_id.text_input(
            "Geçmişini görüntülemek istediğiniz Çiftçi ID", value=_default_farmer_id(), key="history_input"
        )
        limit = col_limit.slider(
            "Kayıt sayısı", min_value=5, max_value=50, value=20, step=5, key="history_limit",
        )
        fetch = col_btn.button("Geçmişi Getir", use_container_width=True, key="history_fetch_button")

    if not fetch:
        return

    if not farmer_id:
        st.warning("Lütfen bir Çiftçi ID girin.")
        return

    token = st.session_state["access_token"]
    result = api_client.get_history(token, farmer_id, limit=limit)
    if not result.ok:
        st.error(f"Geçmiş veriler alınamadı: {result.message}")
        return

    records = result.data
    if not records:
        st.info("Bu çiftçi için sistemde henüz hafıza/geçmiş kaydı bulunmuyor.")
        return

    with st.container(border=True):
        _render_history_trend(records)

    can_modify = st.session_state["role"] in MODIFIER_ROLES

    for record in records:
        ts = datetime.fromisoformat(record["timestamp"]).strftime("%Y-%m-%d %H:%M")
        with st.expander(f"{ts} — {record['crop_type']} — Risk: %{record['disease_probability'] * 100:.0f}"):
            st.markdown(risk_badge_html(record["disease_probability"]), unsafe_allow_html=True)
            st.write(f"**Konum:** {record['location']}")
            st.write(f"**Tahmini verim kaybı:** %{record['estimated_yield_loss_pct']:.1f}")
            if record.get("advice"):
                st.write(f"**Tavsiye:** {record['advice']}")

            if can_modify:
                st.divider()
                _render_record_edit_form(record, token)
                _render_record_delete_control(record, token)


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
