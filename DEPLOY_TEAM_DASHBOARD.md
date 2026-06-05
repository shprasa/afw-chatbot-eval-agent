# Deploy the AFW dashboard for your external team

**Repo:** https://github.com/shprasa/afw-chatbot-eval-agent (public)

The dashboard reads eval CSV exports from this repo. No GitHub token is required for a public repo.

---

## What the team gets

| Item | How they access it |
|------|-------------------|
| **GitHub repo** | https://github.com/shprasa/afw-chatbot-eval-agent — clone, browse data, run agent |
| **Live dashboard** | Streamlit Cloud URL (see Step 3) or run locally |
| **Updates** | Push new CSVs after each eval → dashboard refreshes within ~20 seconds |

---

## Step 1 — Push latest data to GitHub

From your Desktop folder:

```cmd
python push_streamlit_dashboard.py
```

This uploads `streamlit_app.py`, `afw_eval_dashboard/`, `requirements.txt`, and `workspace/powerbi_export/csv/`.

---

## Step 2 — Deploy to Streamlit Cloud (team URL)

1. Go to https://share.streamlit.io and sign in with GitHub
2. **New app** (or edit existing) → repo **`afw-chatbot-eval-agent`**, branch `main`
3. **Main file path:** `streamlit_app.py`
4. **Secrets are optional** for a public repo — the app uses CSVs committed in the repo
5. **Deploy**

Optional secrets (only if you later make the repo private again):

```toml
GITHUB_OWNER = "shprasa"
GITHUB_REPO = "afw-chatbot-eval-agent"
GITHUB_BRANCH = "main"
GITHUB_TOKEN = "ghp_xxxxxxxx"
```

---

## Step 3 — Run locally

```cmd
pip install -r requirements.txt
streamlit run streamlit_app.py --server.port 8502
```

Choose **GitHub (team live)** in the sidebar — works without a token on the public repo.

---

## Hand off to external team

Send them:

1. **GitHub repo URL** — https://github.com/shprasa/afw-chatbot-eval-agent
2. **Streamlit dashboard URL** — your `.streamlit.app` link
3. **`README_HANDOFF.md`** — how to run evals

They do not need collaborator access on a public repo. They do not need your laptop running.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Dashboard empty | Run `python push_readme_to_github.py` after an eval export |
| Streamlit shows old app | Point Streamlit Cloud at `afw-chatbot-eval-agent`, not `afw-chatbot-eval` |
| Data stale | Agent exports → `push_readme_to_github.py` → Streamlit auto-redeploys |
