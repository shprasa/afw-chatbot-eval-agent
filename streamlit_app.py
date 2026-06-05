"""Streamlit Cloud entry — loads eval data from public shprasa/afw-chatbot-eval-agent."""
import os

os.environ.setdefault("GITHUB_OWNER", "shprasa")
os.environ.setdefault("GITHUB_REPO", "afw-chatbot-eval-agent")
os.environ.setdefault("GITHUB_BRANCH", "main")

from afw_eval_dashboard.app import main

main()
