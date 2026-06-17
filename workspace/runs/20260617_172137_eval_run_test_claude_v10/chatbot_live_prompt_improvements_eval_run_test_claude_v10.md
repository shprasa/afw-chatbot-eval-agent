# Prompt Improvement Recommendations

## Data From This Run (with session rationale)
- final outcome accuracy: 0.0%
- recall `insufficient_information`: 0.0%
- recall `manual_review`: n/a
- recall `ineligible`: n/a
- recall `eligible`: n/a
- top confusion: truth `insufficient_information` predicted `manual_review` (7)
- most frequent divergence checkpoint: q8 (7)

## REMOVE — exact clauses from the current system prompt
_Delete these verbatim lines/paragraphs from the prompt file (`/mount/src/afw-chatbot-eval-agent/prompts/prompt_extract_v10.txt`)._

### insufficient_information → manual_review (7 failures)
- REMOVE: `If information is mixed, contradictory, or close to thresholds, default to Manual Review rather than repeated questioning.`

## ADD — exact clauses to insert into the system prompt
_Paste these blocks verbatim into the prompt (Decision Rules + STEP 4 outcome section)._

### Stop escalating missing data to manual_review
- ADD: `If any required screening field is unknown (origin, destination, travel date, mobility, medical stability, companions, financial/compelling need), set `eligibility_outcome` to `insufficient_information`, populate `outcome_reason_codes` with `DATA_INCOMPLETE`, and in `outcome_notes` list only the missing fields. Do NOT set `manual_review` until all required fields are present.`
- ADD: `In `manual_review_rationale`, write "N/A — insufficient_information" when the case is missing required facts.`

### Per-turn rationale requirements (sessionData)
- ADD: `Before each `eligibility_outcome` update, refresh all `*_rationale` fields for criteria touched this turn, plus `outcome_notes` (one sentence: why this outcome now) and `summary_notes` (running screening state).`

## Rationale-driven edits tied to this run
- no per-pattern rationale snippets
