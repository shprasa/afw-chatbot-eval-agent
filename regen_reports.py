"""Regenerate failure + prompt MD reports (no API). Set CHATBOT_OUTPUT_SUFFIX first."""
import os
from chatbot_live_eval import regenerate_iteration_reports_only
if __name__ == '__main__':
    m = regenerate_iteration_reports_only()
    print(m)
