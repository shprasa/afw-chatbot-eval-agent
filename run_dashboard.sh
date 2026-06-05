#!/usr/bin/env bash
# Run in GitHub Codespace or Linux after: pip install -r requirements.txt
set -euo pipefail
cd "$(dirname "$0")"
streamlit run streamlit_app.py --server.enableCORS false --server.enableXsrfProtection false
