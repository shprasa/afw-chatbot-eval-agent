# Prompt Improvement Recommendations

## Data From This Run (with session rationale)
- final outcome accuracy: 56.7%
- recall `insufficient_information`: 46.7%
- recall `manual_review`: 33.3%
- recall `ineligible`: 76.7%
- recall `eligible`: 70.0%
- top confusion: truth `insufficient_information` predicted `manual_review` (15)
- dominant failure reason_code: `DATA_INCOMPLETE` (31 failures)
- most frequent divergence checkpoint: q8 (47)

## REMOVE — exact clauses from the current system prompt
_Delete these verbatim lines/paragraphs from the prompt file (`C:\Users\prasa\OneDrive\Desktop\artifacts\prompt_extract_v1.txt`)._

### insufficient_information → manual_review (15 failures)
- REMOVE: `If information is mixed, contradictory, or close to thresholds, default to Manual Review rather than repeated questioning.`

### manual_review → insufficient_information (10 failures)
- REMOVE: `If criteria are partially met, unclear, or borderline → Manual Review`
- REMOVE: `Manual Review RequiredNon-negotiable criteria passed, but one or more remaining criteria cannot be confidently resolved without human review.`
- REMOVE: `Manual Review is only allowed if both non-negotiable criteria pass.`
- REMOVE: `Timeline is borderline but not disqualifying`

### ineligible softened when hardship/mobility unclear
- REMOVE: `Do not downgrade a user to Not Eligible solely because:`

## ADD — exact clauses to insert into the system prompt
_Paste these blocks verbatim into the prompt (Decision Rules + STEP 4 outcome section)._

### Stop escalating missing data to manual_review
- ADD: `If any required screening field is unknown (origin, destination, travel date, mobility, medical stability, companions, financial/compelling need), set `eligibility_outcome` to `insufficient_information`, populate `outcome_reason_codes` with `DATA_INCOMPLETE`, and in `outcome_notes` list only the missing fields. Do NOT set `manual_review` until all required fields are present.`
- ADD: `In `manual_review_rationale`, write "N/A — insufficient_information" when the case is missing required facts.`

### Borderline-but-complete cases must be manual_review
- ADD: `When origin, destination, date, mobility, and medical stability are described but judgment is needed (seatbelt extender, mental health uncertainty, borderline notice, companion/animal constraints), set `eligibility_outcome` to `manual_review` and cite the specific criterion in `manual_review_rationale` and matching `*_rationale` fields.`

### Safety deferral instead of hard approve/deny
- ADD: `If operational feasibility or medical safety cannot be confirmed from the transcript, set `eligibility_outcome` to `manual_review` (not `eligible` or `ineligible`). Document the uncertainty in `manual_review_rationale` and the relevant criterion rationale field.`

### Commit to ineligible when disqualifier is confirmed
- ADD: `When a non-negotiable disqualifier is confirmed (unsupported reason for travel, out-of-region, funeral/bereavement, distance beyond limits, confirmed financial means), set `eligibility_outcome` to `ineligible` with `REASON_FOR_TRAVEL_NOT_ELIGIBLE` or the matching code even if optional fields remain unknown.`

### Do not ineligible on missing facts alone
- ADD: `Do not set `ineligible` when the only issue is missing information. Use `insufficient_information` until disqualifying facts are confirmed.`

### Eligible gate
- ADD: `Set `eligibility_outcome` to `eligible` only when: (1) reason for travel and geography/distance pass, (2) timeline, mobility, medical stability, and financial/compelling need are satisfied, and (3) no manual-review trigger is active. Otherwise use `insufficient_information` or `manual_review`.`

### Per-turn rationale requirements (sessionData)
- ADD: `Before each `eligibility_outcome` update, refresh all `*_rationale` fields for criteria touched this turn, plus `outcome_notes` (one sentence: why this outcome now) and `summary_notes` (running screening state).`

## Rationale-driven edits tied to this run
### Pattern truth `insufficient_information` → `manual_review`
- observed: F061: reason_codes: DATA_INCOMPLETE | outcome_notes: Insufficient information: trip purpose, route, and eligibility criteria not provided. Chatbot referred for coordinator follow-up. | summary_notes: User inquired about a flight but declined to provide trip reason, route, or details; chatbot explained that a coordinator would reach out for follow-up.
- observed: F062: reason_codes: DATA_INCOMPLETE | outcome_notes: Details needed for travel purpose and destination are missing. Coordinator follow-up required. | summary_notes: User is in Portland, Oregon, needs a flight next month, but declined to provide the reason for travel or destination. Coordinator follow-up is required.
### Pattern truth `manual_review` → `insufficient_information`
- observed: F093: reason_codes: DATA_INCOMPLETE | outcome_notes: Screening not fully complete; user not yet confirmed able to board small plane unassisted and complete application. | summary_notes: User seeks transport from Tucson, AZ to Phoenix, AZ for medical treatment in 12 days; usually able to board small planes unaided but may need a hand on stairs, no nurse required, and faces Medicaid financial gaps; not a DV situation.
- observed: F093 @ q1: reason_codes: DATA_INCOMPLETE
### Pattern truth `eligible` → `manual_review`
- observed: F038: reason_codes: EDGE_CASE_COMPLEX | outcome_notes: Domestic violence relocation scenario with advocate assigned; routed for manual review for further processing. | summary_notes: User requests DV shelter relocation flight from San Diego to Phoenix. Has shelter advocate, no funds, can walk, no medical monitoring needed, appointment in 11 days. Passenger number still pending.
- observed: F038 @ q1: reason_codes: DATA_INCOMPLETE
### Pattern truth `manual_review` → `eligible`
- observed: F101: outcome_notes: All criteria met for commercial airline ticket for medical treatment; financial need, medical stability, and mobility confirmed. | summary_notes: User needs to fly from Honolulu, HI to San Francisco, CA for oncology. Is mobile, does not need medical monitoring, and reported hardship due to 'island costs'. Spouse will accompany. | service_region_rationale: Honolulu, HI and San Francisco, CA are both within Angel Flight West's service region; this was confirmed by the user.
- observed: F101 @ q1: reason_codes: DATA_INCOMPLETE
