# Prompt Improvement Recommendations

## Data From This Run (with session rationale)
- personas: 5 (workbook `AFW_120_User_Test_Cases_Original_Style_Short`)
- scored final outcomes: 0
- unscored final outcomes: 5
- final outcome accuracy: n/a
- truth class distribution: `insufficient_information` 5 (100% of personas); `eligible` 0; `ineligible` 0; `manual_review` 0
- recall `insufficient_information`: 0.0% (0 correct of 5 in class)
- recall `manual_review`: n/a
- recall `ineligible`: n/a
- recall `eligible`: n/a
- question-level checkpoints scored: 0 (question-level accuracy: n/a)
- top confusion pairs: none recorded (0 pairs)
- dominant failure reason_code: none recorded (0 failures with reason codes)
- most frequent divergence checkpoint: none recorded (0 checkpoint divergences)
- mismatch samples with session rationale: 0

This run is entirely `insufficient_information` ground truth, but no final outcomes were scored. Per the run encoding rule, chatbot turns ending in `insufficient_information` or `manual_review` are treated as skip (not scored as incorrect). With 0 scored outcomes and 0.0% recall on `insufficient_information`, this run does not surface a ranked confusion pattern or rationale-backed failure profile to drive targeted prompt surgery.

## REMOVE — exact clauses from the current system prompt
_Delete these verbatim lines/paragraphs from the prompt file (`/mount/src/afw-chatbot-eval-agent/prompts/prompt_extract_v10.txt`)._

- No high-confidence removals identified from this run's error profile.

No confusion pairs were observed (0 truth→predicted mismatches with counts). Without a dominant misclassification pattern, no prompt clause can be tied to a specific failure count from this run.

## ADD — exact clauses to insert into the system prompt
_Paste these blocks verbatim into the prompt (Decision Rules + STEP 4 outcome section)._

### Per-turn rationale requirements (sessionData)
- ADD: `Before each `eligibility_outcome` update, refresh all `*_rationale` fields for criteria touched this turn, plus `outcome_notes` (one sentence: why this outcome now) and `summary_notes` (running screening state).`

No additional ADD blocks are supported by this run's data. With 0 recorded reason codes, 0 checkpoint divergences, and 0 mismatch samples, there is no evidence to justify outcome-routing clauses (e.g., insufficient_information vs manual_review gates) at this sample size.

## Rationale-driven edits tied to this run
- no per-pattern rationale snippets

All 5 personas carry truth label `insufficient_information`, but the payload contains 0 mismatch samples, 0 confusion pairs, and 0 session rationale excerpts (`outcome_notes`, `summary_notes`, reason codes). Re-run with a larger scored sample—or ensure final outcomes resolve to `eligible`/`ineligible` where appropriate—before applying pattern-specific REMOVE/ADD edits beyond the per-turn rationale requirement above.