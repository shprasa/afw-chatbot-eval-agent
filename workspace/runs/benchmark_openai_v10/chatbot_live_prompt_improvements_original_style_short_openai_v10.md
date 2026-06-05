# Prompt Improvement Recommendations

## Data From This Run (with session rationale)
- final outcome accuracy: 61.7%
- recall `insufficient_information`: 63.3%
- recall `manual_review`: 46.7%
- recall `ineligible`: 80.0%
- recall `eligible`: 56.7%
- top confusion: truth `insufficient_information` predicted `manual_review` (9)
- dominant failure reason_code: `DATA_INCOMPLETE` (28 failures)
- most frequent divergence checkpoint: q7 (37)

## REMOVE — exact clauses from the current system prompt
_Delete these verbatim lines/paragraphs from the prompt file (`C:\Users\prasa\OneDrive\Desktop\artifacts\prompt_extract_v1.txt`)._

### insufficient_information → manual_review (9 failures)
- REMOVE: `If information is mixed, contradictory, or close to thresholds, default to Manual Review rather than repeated questioning.`

### manual_review → insufficient_information (7 failures)
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
- observed: F061: reason_codes: DATA_INCOMPLETE | outcome_notes: Trip purpose, origin, destination, and other key info not provided; coordinator follow-up needed. | summary_notes: User asked about help with a flight but did not specify reason for travel, cities, or dates. Unclear if DV or medical context. User may have mobility challenges.
- observed: F061 @ q5: reason_codes: DATA_INCOMPLETE
### Pattern truth `eligible` → `insufficient_information`
- observed: F031: reason_codes: DATA_INCOMPLETE | outcome_notes: Screening is in progress; agent requested info about travel companions. Final eligibility determination not yet reached. | summary_notes: User seeks transport from Fresno, CA to Los Angeles, CA for cancer treatment at UCLA; can walk independently, needs travel in 10 days, has financial hardship, no medical monitoring needed.
- observed: F031 @ q1: reason_codes: DATA_INCOMPLETE
### Pattern truth `manual_review` → `insufficient_information`
- observed: F096: reason_codes: DATA_INCOMPLETE | outcome_notes: Chatbot is still in the process of confirming in-flight medical needs before eligibility outcome. | summary_notes: User requests a flight from Carson City, NV to Sacramento, CA in about 9 days for cardiology, reports independent mobility, has financial need, and is not a DV case. Awaiting response regarding in-flight medical needs before completing screening.
- observed: F096 @ q1: reason_codes: DATA_INCOMPLETE
### Pattern truth `manual_review` → `eligible`
- observed: F097: outcome_notes: User meets criteria for a volunteer-pilot flight: appropriate distance, advance notice, medical stability, mobility, and compelling need. | summary_notes: User inquired about travel from Idaho Falls, ID to Seattle, WA for MS clinic in 14 days. They confirmed ability to transfer/walk independently, have manageable panic, no DV context, and cited rural hardship. Agent indicated eligibility and directed user to application. | service_region_rationale: Both Idaho and Washington are within AFW’s service region. User specified Idaho Falls, ID to Seattle, WA.
- observed: F097 @ q1: reason_codes: DATA_INCOMPLETE
