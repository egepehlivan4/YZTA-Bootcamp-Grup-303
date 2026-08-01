"""
FloraGuard — Arayüz Stil Yardımcıları
Streamlit'in varsayılan görünümünü, ürünün "tarım/yeşil" kimliğine uygun,
kart tabanlı ve daha profesyonel bir düzene taşıyan CSS enjeksiyonu ile
risk seviyesini görsel olarak sınıflandıran yardımcı fonksiyonu barındırır.
"""

from __future__ import annotations

import streamlit as st

_CUSTOM_CSS = """
<style>
    .block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 1100px; }

    /* Üst başlık şeridi */
    .fg-hero {
        background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 55%, #43a047 100%);
        border-radius: 16px;
        padding: 1.75rem 2rem;
        color: #ffffff;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 18px rgba(27, 94, 32, 0.25);
    }
    .fg-hero h1 { margin: 0; font-size: 1.9rem; }
    .fg-hero p { margin: 0.35rem 0 0 0; opacity: 0.92; font-size: 0.98rem; }

    /* Genel kart görünümü */
    .fg-card {
        background: var(--background-color, #ffffff);
        border: 1px solid rgba(46, 125, 50, 0.15);
        border-radius: 14px;
        padding: 1.4rem 1.6rem;
        box-shadow: 0 1px 6px rgba(0, 0, 0, 0.05);
        margin-bottom: 1rem;
    }

    /* Risk rozeti */
    .fg-risk-badge {
        display: inline-block;
        padding: 0.3rem 0.9rem;
        border-radius: 999px;
        font-weight: 600;
        font-size: 0.85rem;
        letter-spacing: 0.02em;
    }
    .fg-risk-low { background: #e8f5e9; color: #1b5e20; }
    .fg-risk-medium { background: #fff8e1; color: #8d6e00; }
    .fg-risk-high { background: #fdecea; color: #b71c1c; }

    /* Tavsiye kutusu */
    .fg-advice {
        background: #f1f8f2;
        border-left: 4px solid #2e7d32;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        font-size: 0.98rem;
        line-height: 1.55;
    }

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
