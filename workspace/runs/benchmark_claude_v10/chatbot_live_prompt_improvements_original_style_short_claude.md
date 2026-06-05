# Prompt Improvement Recommendations

## Data From This Run (with session rationale)
- final outcome accuracy: 65.0%
- recall `insufficient_information`: 76.7%
- recall `manual_review`: 40.0%
- recall `ineligible`: 70.0%
- recall `eligible`: 73.3%
- top confusion: truth `manual_review` predicted `insufficient_information` (10)
- dominant failure reason_code: `DATA_INCOMPLETE` (17 failures)
- most frequent divergence checkpoint: q7 (37)

## REMOVE — exact clauses from the current system prompt
_Delete these verbatim lines/paragraphs from the prompt file (`C:\Users\prasa\OneDrive\Desktop\artifacts\prompt_extract_v1.txt`)._

### insufficient_information → manual_review (7 failures)
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

### Eligible gate
- ADD: `Set `eligibility_outcome` to `eligible` only when: (1) reason for travel and geography/distance pass, (2) timeline, mobility, medical stability, and financial/compelling need are satisfied, and (3) no manual-review trigger is active. Otherwise use `insufficient_information` or `manual_review`.`

### Per-turn rationale requirements (sessionData)
- ADD: `Before each `eligibility_outcome` update, refresh all `*_rationale` fields for criteria touched this turn, plus `outcome_notes` (one sentence: why this outcome now) and `summary_notes` (running screening state).`

## Rationale-driven edits tied to this run
### Pattern truth `manual_review` → `insufficient_information`
- observed: F091: reason_codes: DATA_INCOMPLETE, MOBILITY_CRITERIA_NOT_MET | outcome_notes: Screening session was incomplete. Key details still needed include: mobility assessment (wheelchair user, may need step assistance), presence of service animal or pet, financial need, and exact travel date. Medically stable, route and timing are within AFW parameters. | summary_notes: User is a patient traveling from Sacramento, CA to Los Angeles, CA for medical treatment approximately 10 days from now. They will be accompanied by a partner. User uses a wheelchair and may need help with one step. They stated they are medically stable and do not require monitoring. User explicitly noted this is not a DV case. Session was still in progress when extraction was requested — questions about service animal/pet and financial need had not yet been answered.
- observed: F091 @ q1: reason_codes: DATA_INCOMPLETE
### Pattern truth `insufficient_information` → `manual_review`
- observed: F066: reason_codes: DATA_INCOMPLETE | outcome_notes: User was unable or unwilling to provide basic travel details (origin, destination, travel date). The chatbot was unable to complete the eligibility screening. Case escalated to a human coordinator for follow-up. | summary_notes: User initiated a chat requesting help with travel, possibly for a medical appointment. When asked for origin/destination cities and states, the user gave vague, non-committal responses ("Not sure," "Maybe," "Depends," "Probably fine"). Travel date was also unknown. The chatbot was unable to gather sufficient information to conduct a screening and escalated the case to a human coordinator.
- observed: F068: reason_codes: DATA_INCOMPLETE | outcome_notes: User was unable or unwilling to provide origin and destination locations. Without this critical information, service region, distance, pathway, and notice requirements could not be assessed. Chatbot referred the case to a coordinator for follow-up. | summary_notes: User initiated a request for a flight for a health-related appointment. When asked for origin and destination cities and states, the user repeatedly deflected with responses like "Skip," "Between two cities," and "TBD." The user also mentioned uncertainty about "inflight care." The chatbot was unable to complete the eligibility screening due to missing location data and escalated to a coordinator.
### Pattern truth `ineligible` → `insufficient_information`
- observed: F015: reason_codes: DATA_INCOMPLETE | outcome_notes: Session was still in progress at the time of extraction. Travel date was vague ("Monday"), exact notice days could not be confirmed, and the conversation had not yet reached a final eligibility determination. Commercial pathway likely given HI-CA route. | summary_notes: Passenger is traveling from Honolulu, HI to San Francisco, CA to see a mainland specialist. Travel is requested for "Monday." Passenger is mobile, medically stable (no in-flight monitoring needed), and will have one companion. No prior Angel Flight West travel this year. User indicated no travel funds available. DV context was explicitly ruled out. Session ended mid-screening with a question about pets/service animals still pending.
- observed: F015 @ q1: reason_codes: DATA_INCOMPLETE
### Pattern truth `eligible` → `ineligible`
- observed: F036: reason_codes: INSUFFICIENT_NOTICE | outcome_notes: Patient is otherwise a strong candidate (medical need, financial need via SSDI, mobile, medically stable, within service region), but the appointment is only 3 days away, which does not meet the 5 business day minimum notice requirement for volunteer pilot flights. | summary_notes: Patient is traveling from Redding, CA to Sacramento, CA for a burn clinic follow-up appointment. They are on SSDI, mobile, traveling solo, and do not require medical monitoring. The only barrier is insufficient notice — the appointment is 3 days away, and volunteer flights require at least 5 business days of lead time. The chatbot referred the user to Air Care Alliance for shorter-notice options.
- observed: F036 @ q1: reason_codes: DATA_INCOMPLETE
