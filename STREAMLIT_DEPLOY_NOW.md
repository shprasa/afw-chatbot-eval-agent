# Fix "You do not have access to this app"

The old URL **afw-chatbot-eval.streamlit.app** was created under a **different Streamlit login** (not your current `shdprasad@ucdavis.edu` + `shprasa` combo). You cannot take over that URL — deploy a **new app** on your account instead.

---

## Deploy in 2 minutes (your account)

1. Open **https://share.streamlit.io** while signed in as **shdprasad@ucdavis.edu** with GitHub **shprasa** connected.

2. Click **Create app** (top right).

3. Fill in:

   | Field | Value |
   |-------|-------|
   | Repository | `shprasa/afw-chatbot-eval-agent` |
   | Branch | `main` |
   | Main file path | `streamlit_app.py` |
   | App URL (optional) | e.g. `afw-eval-dashboard` → `https://afw-eval-dashboard.streamlit.app` |

4. **Advanced settings** → Python version **3.10** or **3.11** (not 3.13+ if offered).

5. **Secrets** → leave **empty** (repo is public; data is in the repo).

6. Click **Deploy**.

7. Wait ~2 minutes. You should see:
   - Title: **Angel Flight West — Eval Dashboard**
   - Sidebar: **4 evaluation runs**
   - Tabs: Executive, Persona, Conversations, Statistics, Gold Test Cases

---

## If GitHub is not connected to Streamlit

1. Streamlit Cloud → **Settings** → **Linked accounts**
2. Connect **github.com/shprasa**
3. Grant access to repo **`afw-chatbot-eval-agent`** (public repos are usually visible automatically)

---

## Share with your team

Send them the **new** `.streamlit.app` URL from step 6.  
Repo (public, no login needed): https://github.com/shprasa/afw-chatbot-eval-agent

---

## Update data after eval runs

On your Desktop:

```cmd
python push_streamlit_dashboard.py
```

Then in Streamlit Cloud: **⋮ → Reboot app** (or wait for auto-redeploy).

---

## Ignore the old URL

**https://afw-chatbot-eval.streamlit.app** — not on your account; do not use for handoff.
