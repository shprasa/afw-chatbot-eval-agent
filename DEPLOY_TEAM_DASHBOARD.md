# AFW Hosted Platform — Deploy for your team

**One Streamlit app** serves both the **Dashboard** and **Eval Agent**. No local terminal required.

| Page | Purpose |
|------|---------|
| **Dashboard** | Live charts from `workspace/powerbi_export/csv/` |
| **Eval Agent** | Run evals, McNemar tests, save to GitHub |

---

## Deploy on Streamlit Cloud

1. https://share.streamlit.io → sign in with GitHub
2. **New app** → repo `shprasa/afw-chatbot-eval-agent`, branch `main`
3. **Main file:** `streamlit_app.py`
4. **Secrets:**

```toml
GITHUB_TOKEN = "token-with-repo-write"
GITHUB_OWNER = "shprasa"
GITHUB_REPO = "afw-chatbot-eval-agent"
GITHUB_BRANCH = "main"
```

5. Deploy → share the `.streamlit.app` URL with your team

---

## Team workflow

1. Open **Eval Agent** → run evaluation
2. Click **Save to GitHub repo**
3. Open **Dashboard** → data updates (auto-refresh every 20 min, or reload)

---

## Manual push from Desktop (optional)

```cmd
python push_streamlit_dashboard.py
```
