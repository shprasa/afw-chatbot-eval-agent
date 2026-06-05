"""AFW hosted app — Dashboard + Eval Agent (Streamlit Cloud)."""
import os

os.environ.setdefault("GITHUB_OWNER", "shprasa")
os.environ.setdefault("GITHUB_REPO", "afw-chatbot-eval-agent")
os.environ.setdefault("GITHUB_BRANCH", "main")

import streamlit as st

st.set_page_config(
    page_title="AFW Eval Platform",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

dash = st.Page(
    "afw_eval_dashboard/app.py",
    title="Dashboard",
    icon="📊",
    default=True,
    url_path="Dashboard",
)
agent = st.Page(
    "afw_eval_agent_ui/app.py",
    title="AFW Screening Chatbot Evaluation Agent",
    icon="🛠️",
    url_path="Eval_Agent",
)

nav = st.navigation([dash, agent])
nav.run()
