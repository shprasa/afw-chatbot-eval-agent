# Prompt Improvement Recommendations

## Data From This Run (with session rationale)
- final outcome accuracy: 66.7%
- recall `insufficient_information`: 83.3%
- recall `manual_review`: 46.7%
- recall `ineligible`: 66.7%
- recall `eligible`: 70.0%
- top confusion: truth `manual_review` predicted `insufficient_information` (10)
- dominant failure reason_code: `DATA_INCOMPLETE` (19 failures)
- most frequent divergence checkpoint: q7 (39)

## REMOVE — exact clauses from the current system prompt
_Delete these verbatim lines/paragraphs from the prompt file (`C:\Users\prasa\OneDrive\Desktop\artifacts\prompt_extract_v1.txt`)._

### insufficient_information → manual_review (5 failures)
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
- observed: F093: reason_codes: DATA_INCOMPLETE | outcome_notes: Screening was not completed. Key questions about mobility (unassisted boarding) and medical equipment needs (oxygen) were not fully resolved before the session ended. Financial need (Medicaid gaps) and route are favorable. Manual review or follow-up needed. | summary_notes: User is seeking travel from Tucson, AZ to Phoenix, AZ for medical treatment approximately 12 days out. User clarified this is not a domestic violence case. Mentioned Medicaid gaps as a financial need. A sister may travel as a companion. Passenger may need a hand on stairs but stated no nurse is needed. Questions about oxygen/medical equipment and companion were unanswered at extraction time.
- observed: F093 @ q1: reason_codes: DATA_INCOMPLETE
### Pattern truth `ineligible` → `insufficient_information`
- observed: F015: reason_codes: DATA_INCOMPLETE | outcome_notes: The chatbot had not yet reached a final eligibility conclusion. Key missing information includes: confirmation of user role (patient vs. caregiver), exact travel date, and whether minimum notice requirements are met. The conversation ended mid-screening. | summary_notes: User is traveling from Honolulu, HI to San Francisco, CA for a specialist medical appointment. They mentioned traveling with one companion, no in-flight monitoring needed, no travel funds, and explicitly stated the trip is not DV-related. The exact Monday travel date was not confirmed. The chatbot was still gathering information when the extract was requested.
- observed: F015 @ q1: reason_codes: DATA_INCOMPLETE
### Pattern truth `eligible` → `ineligible`
- observed: F036: reason_codes: INSUFFICIENT_NOTICE | outcome_notes: Patient is traveling from Redding to Sacramento for a burn clinic follow-up. Meets mobility, medical stability, and financial need criteria. However, the appointment is only 3 days away, which does not meet the minimum 5-business-day notice requirement for the volunteer pilot pathway. User was referred to Air Care Alliance for shorter-notice options. | summary_notes: A patient on SSDI is seeking a flight from Redding, CA to Sacramento, CA for a burn clinic follow-up appointment. The user is independently mobile, does not require medical monitoring, and will travel solo. Financial need is established via SSDI. The only disqualifying factor is the 3-day notice — insufficient for the volunteer pilot program. User was referred to Air Care Alliance and encouraged to contact AFW for future appointments with more lead time.
- observed: F036 @ q1: reason_codes: DATA_INCOMPLETE
### Pattern truth `insufficient_information` → `manual_review`
- observed: F066: reason_codes: DATA_INCOMPLETE | outcome_notes: User was unable or unwilling to provide key details (origin, destination, travel date) needed to complete screening. Chatbot referred the case to a coordinator for follow-up. | summary_notes: User initiated a conversation about travel assistance but provided very vague responses throughout. They indicated the travel was to see a doctor but could not or would not provide origin city/state, destination city/state, or travel date. The chatbot was unable to complete the eligibility screening and offered to connect the user with a coordinator.
- observed: F070: reason_codes: DATA_INCOMPLETE | outcome_notes: Origin and destination are unknown; full eligibility screening could not be completed. Chatbot referred the case for manual coordinator review and asked the user for contact information. | summary_notes: User reached out with a potential domestic violence relocation request. They were vague throughout the conversation, unable to provide origin, destination, or travel date. The chatbot repeatedly asked for location details but received non-specific responses such as "Mountain area," "Pending," and "Unknown." The chatbot concluded the screening could not be completed and flagged the case for manual coordinator review.
