"""Regenerate failure + prompt reports for Claude v1 eval (no API calls)."""
import os

os.environ["CHATBOT_OUTPUT_SUFFIX"] = "_original_style_short_claude_v1"
os.environ["CHATBOT_REGEN_REPORTS_ONLY"] = "1"

from chatbot_live_eval import regenerate_iteration_reports_only

if __name__ == "__main__":
    metrics = regenerate_iteration_reports_only()
    print("done", metrics.get("n_scored"), "scored", metrics.get("final_outcome_accuracy"))
