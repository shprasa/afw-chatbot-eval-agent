"""AFW dashboard visual theme and Plotly styling."""
from __future__ import annotations

import plotly.graph_objects as go
import plotly.io as pio

BRAND = {
    "navy": "#1B3A5C",
    "sky": "#2E6DA4",
    "gold": "#C9A227",
    "success": "#1F7A4C",
    "warning": "#B45309",
    "danger": "#B91C1C",
    "muted": "#64748B",
    "bg": "#F8FAFC",
    "card": "#FFFFFF",
}

MODEL_COLORS = {
    "OpenAI": "#2563EB",
    "Claude": "#EA580C",
    "openai": "#2563EB",
    "claude": "#EA580C",
}

OUTCOME_COLORS = {
    "Eligible": "#1F7A4C",
    "Ineligible": "#B91C1C",
    "Manual Review": "#B45309",
    "Insufficient Information": "#64748B",
}

PLOTLY_TEMPLATE = go.layout.Template(
    layout=go.Layout(
        font=dict(family="Inter, Segoe UI, sans-serif", color=BRAND["navy"], size=13),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        colorway=[BRAND["sky"], BRAND["gold"], BRAND["success"], BRAND["danger"], BRAND["muted"]],
        margin=dict(l=24, r=24, t=48, b=24),
        title=dict(font=dict(size=16, color=BRAND["navy"])),
        xaxis=dict(gridcolor="#E2E8F0", linecolor="#CBD5E1"),
        yaxis=dict(gridcolor="#E2E8F0", linecolor="#CBD5E1"),
        legend=dict(bgcolor="rgba(255,255,255,0.8)", bordercolor="#E2E8F0"),
    )
)

pio.templates["afw"] = PLOTLY_TEMPLATE
pio.templates.default = "afw"


def inject_css() -> None:
    import streamlit as st

    st.markdown(
        f"""
        <style>
        .block-container {{ padding-top: 1.2rem; padding-bottom: 2rem; max-width: 1400px; }}
        [data-testid="stMetricValue"] {{ font-size: 1.75rem; font-weight: 700; color: {BRAND['navy']}; }}
        [data-testid="stMetricLabel"] {{ font-size: 0.85rem; color: {BRAND['muted']}; }}
        .afw-hero {{
            background: linear-gradient(135deg, {BRAND['navy']} 0%, {BRAND['sky']} 100%);
            color: white; padding: 1.25rem 1.5rem; border-radius: 12px; margin-bottom: 1rem;
        }}
        .afw-hero h1 {{ color: white !important; font-size: 1.5rem; margin: 0; }}
        .afw-hero p {{ color: #E2E8F0; margin: 0.35rem 0 0; font-size: 0.95rem; }}
        .afw-insight {{
            background: {BRAND['card']}; border-left: 4px solid {BRAND['gold']};
            padding: 0.85rem 1rem; border-radius: 0 8px 8px 0; margin: 0.5rem 0 1rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        }}
        .afw-insight strong {{ color: {BRAND['navy']}; }}
        div[data-testid="stTabs"] button {{ font-weight: 600; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def hero(title: str, subtitle: str) -> None:
    import streamlit as st

    st.markdown(
        f'<div class="afw-hero"><h1>{title}</h1><p>{subtitle}</p></div>',
        unsafe_allow_html=True,
    )


def insight(text: str) -> None:
    import streamlit as st

    st.markdown(f'<div class="afw-insight">{text}</div>', unsafe_allow_html=True)
