# Deploy the AFW dashboard for your external team

**Goal:** Give your team a **shared URL** that shows live eval results — not `localhost` on your machine.

The recommended path is **Streamlit Community Cloud** (free). It reads CSV exports from your private GitHub repo on every refresh.

---

## What the team gets

| Item | How they access it |
|------|-------------------|
| **Live dashboard** | Public Streamlit URL (e.g. `https://afw-eval-dashboard.streamlit.app`) |
| **Eval agent + data** | GitHub repo `shprasa/afw-chatbot-eval-agent` (add them as collaborators) |
| **Updates** | Automatic — agent exports CSVs → dashboard refreshes within ~20 seconds |

---

## Step 1 — Push dashboard files to GitHub

From your Desktop folder:

```cmd
python push_readme_to_github.py
```

This uploads `streamlit_app.py`, `afw_eval_dashboard/`, `requirements.txt`, and the latest `workspace/powerbi_export/csv/` files.

---

## Step 2 — Add GitHub collaborators (agent handoff)

1. Open https://github.com/shprasa/afw-chatbot-eval-agent/settings/access
2. **Invite collaborators** → add each teammate's GitHub username
3. They can clone the repo and run the agent locally, or rely on your scheduled runs + the live dashboard

---

## Step 3 — Deploy to Streamlit Cloud

1. Go to https://share.streamlit.io and sign in with GitHub
2. **New app** → pick repo `afw-chatbot-eval-agent`, branch `main`
3. **Main file path:** `streamlit_app.py`
4. Click **Advanced settings** → add Python 3.10+ if needed
5. Under **Secrets**, paste (use a **read-only** fine-grained token scoped to this repo):

```toml
GITHUB_TOKEN = "ghp_xxxxxxxx"
GITHUB_OWNER = "shprasa"
GITHUB_REPO = "afw-chatbot-eval-agent"
GITHUB_BRANCH = "main"

# Optional — share this password only with your team (hides dashboard from random visitors)
TEAM_PASSWORD = "choose-a-strong-password"
```

6. **Deploy**

When the app is live, copy the `.streamlit.app` URL and send it to your team.

---

## Step 4 — Share with the external team

Send them:

1. **Dashboard URL** — the Streamlit link (and optional `TEAM_PASSWORD` if you set one)
2. **GitHub repo** — after they accept the collaborator invite
3. **Handoff doc** — `README_HANDOFF.md` in the repo for running evals

They do **not** need Power BI or your laptop running. The dashboard pulls from GitHub.

---

## Optional — run locally with GitHub live mode

If a teammate prefers a local copy:

```cmd
pip install -r requirements.txt
streamlit run streamlit_app.py --server.port 8502
```

In the sidebar, choose **GitHub (team live)**. Locally, credentials come from `github_publish_config.txt` (never commit that file).

---

## Security checklist (before handoff)

- [ ] Create a **fine-grained GitHub token** with read-only access to `afw-chatbot-eval-agent` for Streamlit secrets
- [ ] **Revoke** any old tokens pasted into `github_publish_config.txt` on your Desktop
- [ ] Set `TEAM_PASSWORD` in Streamlit secrets if the app URL should not be open to the public
- [ ] Confirm `github_publish_config.txt` is **not** in the GitHub repo

---

## Power BI (optional, not required for team access)

Power BI Desktop still works for static executive decks. For **live team monitoring**, use the Streamlit URL above. See `workspace/powerbi_export/POWERBI_Setup_Guide.md` if needed.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Dashboard empty | Run an eval (agent menu 1) so CSVs exist under `workspace/powerbi_export/csv/` |
| GitHub auth error on Cloud | Check `GITHUB_TOKEN` in Streamlit secrets; token needs `Contents: Read` on the repo |
| Team cannot clone repo | Add them under repo **Settings → Collaborators** |
| Data stale | Agent must push exports (`push_readme_to_github.py` or your publish script after each run) |
