"""
FloraGuard — Arayüz Stil Yardımcıları
Streamlit'in varsayılan görünümünü, ürünün "tarım/lüks" kimliğine uygun,
zümrüt yeşili + altın vurgulu, kart tabanlı bir düzene taşıyan CSS enjeksiyonu
ile risk seviyesini görsel olarak sınıflandıran yardımcı fonksiyonu barındırır.

Mimari not: Kartlar için `st.container(border=True)` kullanılmalı, HAM
`st.markdown('<div>...')` + widget'lar + `st.markdown('</div>')` deseni
KULLANILMAMALI — Streamlit'te her `st.markdown`/widget çağrısı kendi bağımsız
element konteynerini oluşturur; markdown'dan gelen açma/kapama div'leri bu
konteynerleri gerçekten SARMALAMAZ (DOM'da kardeş elemanlar olarak kalır).
Bu, görsel "kayma"/kırık kutu render'ının kök nedeniydi. `st.container(border=True)`
gerçek bir DOM sarmalayıcısı ürettiği için, tüm bordered container'ları TEK
noktadan (aşağıdaki `[data-testid="stVerticalBlockBorderWrapper"]` seçicisi)
restyle ediyoruz.
"""

from __future__ import annotations

import streamlit as st

_CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Inter:wght@400;500;600;700&display=swap');

:root {
    --fg-emerald-900: #0b2e22;
    --fg-emerald-700: #0f4636;
    --fg-emerald-500: #16664f;
    --fg-gold-500: #c8a24a;
    --fg-gold-300: #e3c877;
}

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.block-container { padding-top: 1.75rem; padding-bottom: 3rem; max-width: 1120px; }

h1, h2, h3, h4 { font-family: 'Playfair Display', serif !important; letter-spacing: 0.01em; }

/* Üst başlık şeridi — koyu zümrüt + altın vurgu */
.fg-hero {
    background: linear-gradient(135deg, var(--fg-emerald-900) 0%, var(--fg-emerald-700) 55%, var(--fg-emerald-500) 100%);
    border-radius: 18px;
    padding: 2.1rem 2.4rem;
    color: #f6f1e4;
    margin-bottom: 1.75rem;
    box-shadow: 0 10px 30px rgba(11, 46, 34, 0.35);
    border: 1px solid rgba(200, 162, 74, 0.35);
    position: relative;
    overflow: hidden;
}
.fg-hero::after {
    content: "";
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at 85% -10%, rgba(200, 162, 74, 0.25), transparent 55%);
    pointer-events: none;
}
.fg-hero h1 {
    margin: 0;
    font-size: 2.1rem;
    color: #f6f1e4 !important;
    display: flex;
    align-items: center;
    gap: 0.6rem;
}
.fg-hero p {
    margin: 0.5rem 0 0 0;
    opacity: 0.88;
    font-size: 1rem;
    max-width: 46rem;
    font-family: 'Inter', sans-serif;
}
.fg-hero .fg-hero-badge {
    display: inline-block;
    margin-top: 0.9rem;
    padding: 0.25rem 0.8rem;
    border-radius: 999px;
    background: rgba(200, 162, 74, 0.18);
    border: 1px solid rgba(227, 200, 119, 0.55);
    color: var(--fg-gold-300);
    font-size: 0.78rem;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}

/* st.container(border=True) -> tüm "kart" görünümü TEK noktadan buradan gelir */
div[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 16px !important;
    border: 1px solid rgba(15, 70, 54, 0.14) !important;
    box-shadow: 0 2px 14px rgba(11, 46, 34, 0.06);
    background: var(--background-color);
    transition: box-shadow 0.2s ease;
}
div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    box-shadow: 0 6px 22px rgba(11, 46, 34, 0.10);
}

/* Sidebar — koyu zümrüt panel */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, var(--fg-emerald-900) 0%, #0d3327 100%);
}
section[data-testid="stSidebar"] * { color: #f0ece0 !important; }
section[data-testid="stSidebar"] hr { border-color: rgba(227, 200, 119, 0.25); }

/* Butonlar */
.stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"] {
    background: linear-gradient(135deg, var(--fg-emerald-700), var(--fg-emerald-500));
    border: 1px solid var(--fg-gold-500);
    color: #f6f1e4;
    font-weight: 600;
    letter-spacing: 0.02em;
    box-shadow: 0 3px 10px rgba(11, 46, 34, 0.25);
    transition: transform 0.12s ease, box-shadow 0.12s ease;
}
.stButton > button[kind="primary"]:hover, .stFormSubmitButton > button[kind="primary"]:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 16px rgba(11, 46, 34, 0.32);
    border-color: var(--fg-gold-300);
}

/* Sekmeler */
.stTabs [data-baseweb="tab-list"] { gap: 0.5rem; border-bottom: 1px solid rgba(15, 70, 54, 0.15); }
.stTabs [data-baseweb="tab"] {
    font-weight: 600;
    font-family: 'Inter', sans-serif;
    padding: 0.6rem 0.2rem;
}
.stTabs [aria-selected="true"] { color: var(--fg-emerald-700) !important; }
.stTabs [data-baseweb="tab-highlight"] { background-color: var(--fg-gold-500) !important; }

/* Metric kartları */
div[data-testid="stMetric"] {
    background: rgba(15, 70, 54, 0.045);
    border: 1px solid rgba(15, 70, 54, 0.10);
    border-radius: 12px;
    padding: 0.85rem 1rem 0.6rem;
}
div[data-testid="stMetricLabel"] { font-weight: 600; opacity: 0.75; }

/* Risk rozeti */
.fg-risk-badge {
    display: inline-block;
    padding: 0.32rem 0.95rem;
    border-radius: 999px;
    font-weight: 700;
    font-size: 0.8rem;
    letter-spacing: 0.03em;
    vertical-align: middle;
}
.fg-risk-low { background: #e5f3ec; color: #0f4636; border: 1px solid #b9ddc9; }
.fg-risk-medium { background: #fbf1de; color: #8a6414; border: 1px solid #ecd8a4; }
.fg-risk-high { background: #fbe9e7; color: #9c2b1f; border: 1px solid #f0bcb4; }

/* Tavsiye kutusu */
.fg-advice {
    background: linear-gradient(135deg, rgba(15, 70, 54, 0.05), rgba(200, 162, 74, 0.06));
    border-left: 4px solid var(--fg-gold-500);
    border-radius: 10px;
    padding: 1.05rem 1.3rem;
    font-size: 0.98rem;
    line-height: 1.6;
}

/* Geçmiş kaydı satırları */
.stExpander { border-radius: 12px !important; border-color: rgba(15, 70, 54, 0.14) !important; }

footer[data-testid="stFooter"], #MainMenu { visibility: hidden; }
</style>
"""


def inject_global_styles() -> None:
    st.markdown(_CUSTOM_CSS, unsafe_allow_html=True)


def risk_level(probability: float) -> tuple[str, str]:
    """0-1 arası olasılığı (etiket, CSS sınıfı) çiftine çevirir."""
    if probability < 0.34:
        return "Düşük Risk", "fg-risk-low"
    if probability < 0.67:
        return "Orta Risk", "fg-risk-medium"
    return "Yüksek Risk", "fg-risk-high"


def risk_badge_html(probability: float) -> str:
    label, css_class = risk_level(probability)
    return f'<span class="fg-risk-badge {css_class}">{label}</span>'
