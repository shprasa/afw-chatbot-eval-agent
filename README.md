# AFW Screening Chatbot Evaluation Platform

**Public repo:** https://github.com/shprasa/afw-chatbot-eval-agent

Hosted **Streamlit app** (no local terminal required):
- **Dashboard** — live eval charts, auto-refreshes every 20 minutes
- **Eval Agent** — run evaluations and McNemar comparisons in the browser

Deploy `streamlit_app.py` on [Streamlit Cloud](https://share.streamlit.io) from this repo.

---

## Quick start (hosted)

1. Open your Streamlit app URL (`.streamlit.app`)
2. Go to **Eval Agent** → run an evaluation or McNemar comparison
3. Click **Save to GitHub repo** when prompted
4. Switch to **Dashboard** — new data appears after refresh (up to 20 min, or reload)

### Streamlit secrets (required for saving to repo)

```toml
GITHUB_TOKEN = "your-token-with-repo-write"
GITHUB_OWNER = "shprasa"
GITHUB_REPO = "afw-chatbot-eval-agent"
GITHUB_BRANCH = "main"
```

---

## What gets saved to the repo

When you choose **Save to GitHub repo**:

```
workspace/
  runs/<run_id>/          predictions, transcripts, reports
  runs/manifest.json      run index
  comparisons/            McNemar outputs (JSON, XLSX, MD)
  powerbi_export/csv/     dashboard data tables
```

The dashboard reads `workspace/powerbi_export/csv/` from this repo.

---

## Local development (optional)

```cmd
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Push updates manually:

```cmd
python push_streamlit_dashboard.py
```

---

## Persona counts

Evaluation runs use **deduplicated predictions** (`persona_id`, keep last) so rerun overlaps do not inflate counts (e.g. 120 personas, not 122).

---

## UC Davis GSM MSBA · Angel Flight West Practicum (2025–2026)
