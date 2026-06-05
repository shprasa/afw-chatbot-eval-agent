"""AFW brand theme — Angel Flight West palette."""
from __future__ import annotations

import plotly.graph_objects as go
import plotly.io as pio

BRAND = {
    "ocean": "#09889e",
    "light_blue": "#79d0e6",
    "navy": "#11487c",
    "bright_red": "#cd2038",
    "coral": "#f15e51",
    "orange": "#f9b13d",
    "charcoal": "#272f35",
    "muted_teal": "#385363",
    "silver": "#c0c1c0",
    "bg": "#f4f8fa",
    "card": "#ffffff",
}

MODEL_COLORS = {
    "OpenAI": BRAND["ocean"],
    "Claude": BRAND["coral"],
    "openai": BRAND["ocean"],
    "claude": BRAND["coral"],
}

OUTCOME_COLORS = {
    "Eligible": BRAND["ocean"],
    "Ineligible": BRAND["bright_red"],
    "Manual Review": BRAND["orange"],
    "Insufficient Information": BRAND["muted_teal"],
}

PLOTLY_TEMPLATE = go.layout.Template(
    layout=go.Layout(
        font=dict(family="Segoe UI, Inter, sans-serif", color=BRAND["charcoal"], size=13),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        colorway=[BRAND["ocean"], BRAND["light_blue"], BRAND["coral"], BRAND["orange"], BRAND["navy"]],
        margin=dict(l=48, r=32, t=56, b=48),
        title=dict(font=dict(size=16, color=BRAND["navy"])),
        xaxis=dict(gridcolor=BRAND["silver"], linecolor=BRAND["silver"], automargin=True),
        yaxis=dict(gridcolor=BRAND["silver"], linecolor=BRAND["silver"], automargin=True),
        legend=dict(bgcolor="rgba(255,255,255,0.9)", bordercolor=BRAND["silver"]),
    )
)

pio.templates["afw"] = PLOTLY_TEMPLATE
pio.templates.default = "afw"

CHART_HEIGHT = 500
CHART_HEIGHT_TALL = 560


def chart_layout(fig, *, height: int | None = None, extra_bottom: int = 0) -> go.Figure:
    fig.update_layout(
        height=height or CHART_HEIGHT,
        margin=dict(l=48, r=32, t=56, b=48 + extra_bottom),
    )
    return fig


def inject_css() -> None:
    import streamlit as st

    st.markdown(
        f"""
        <style>
        .block-container {{ padding-top: 1rem; padding-bottom: 2rem; max-width: 1480px; }}
        [data-testid="stMetricValue"] {{ font-size: 1.6rem; font-weight: 700; color: {BRAND['navy']}; }}
        [data-testid="stMetricLabel"] {{ font-size: 0.85rem; color: {BRAND['muted_teal']}; }}
        .afw-hero {{
            background: linear-gradient(135deg, {BRAND['navy']} 0%, {BRAND['ocean']} 100%);
            color: white; padding: 1rem 1.25rem; border-radius: 10px; margin-bottom: 0.75rem;
        }}
        .afw-hero h1 {{ color: white !important; font-size: 1.35rem; margin: 0; }}
        .afw-hero p {{ color: {BRAND['light_blue']}; margin: 0.3rem 0 0; font-size: 0.9rem; }}
        .afw-insight {{
            background: {BRAND['card']}; border-left: 4px solid {BRAND['orange']};
            padding: 0.75rem 1rem; border-radius: 0 8px 8px 0; margin: 0.5rem 0 0.75rem;
        }}
        div[data-testid="stTabs"] button {{ font-weight: 600; color: {BRAND['navy']}; }}
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


def brand_header(title: str, subtitle: str, logo_path: str | None = None) -> None:
    import streamlit as st

    col_logo, col_txt = st.columns([1, 5])
    with col_logo:
        if logo_path:
            p = __import__("pathlib").Path(logo_path)
            if p.is_file():
                st.image(str(p), width=120)
            else:
                st.markdown(f"<div style='font-size:2.5rem'>✈️</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='font-size:2.5rem'>✈️</div>", unsafe_allow_html=True)
    with col_txt:
        st.markdown(
            f"<h2 style='color:{BRAND['navy']};margin:0'>{title}</h2>"
            f"<p style='color:{BRAND['muted_teal']};margin:0'>{subtitle}</p>",
            unsafe_allow_html=True,
        )
