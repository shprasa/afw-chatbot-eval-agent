# Failure Analysis

## Run Summary
- personas: 120
- scored final outcomes: 120
- final outcome accuracy: 66.7%
- incorrect matches: 40
- unscored final outcomes: 0

## Error Concentration By Truth Class
- manual_review: 16 mismatches
- ineligible: 10 mismatches
- eligible: 9 mismatches
- insufficient_information: 5 mismatches

## Confusion Pairs
- truth `manual_review` predicted `insufficient_information`: 10
- truth `ineligible` predicted `insufficient_information`: 6
- truth `eligible` predicted `ineligible`: 5
- truth `insufficient_information` predicted `manual_review`: 5
- truth `manual_review` predicted `ineligible`: 4
- truth `ineligible` predicted `manual_review`: 3
- truth `eligible` predicted `insufficient_information`: 3
- truth `manual_review` predicted `eligible`: 2
- truth `ineligible` predicted `eligible`: 1
- truth `eligible` predicted `manual_review`: 1

## First Divergence Checkpoint
- q7: 39 mismatches
- q8: 37 mismatches
- q6: 36 mismatches
- q1: 35 mismatches
- q2: 35 mismatches
- q3: 35 mismatches
- q4: 35 mismatches
- q5: 35 mismatches

## Session Rationale — Outcome Reason Codes (failures only)
- `DATA_INCOMPLETE`: 19
- `DISTANCE_TOO_GREAT`: 7
- `OTHER`: 3
- `DATA_INCOMPLETE, FINANCIAL_CRITERIA_NOT_MET`: 3
- `INSUFFICIENT_NOTICE`: 3
- `DATA_INCOMPLETE, EDGE_CASE_COMPLEX`: 2
- `DATA_INCOMPLETE, MOBILITY_CRITERIA_NOT_MET`: 1
- `EDGE_CASE_COMPLEX`: 1
- `FINANCIAL_CRITERIA_NOT_MET, DATA_INCOMPLETE`: 1

## Session Rationale — Final outcome_notes (failures only)
- (1x) The chatbot had not yet reached a final eligibility conclusion. Key missing information includes: confirmation of user role (patient vs. caregiver), exact travel date, and whether minimum notice requirements are met. The conversation ended mid-screening.
- (1x) Screening is incomplete. Mobility status is unclear due to post-amputation non-weight-bearing condition. Medical stability during flight has not yet been confirmed. Coordinator follow-up needed.
- (1x) Screening was still in progress at the end of the conversation. The user clarified they are the caregiver (parent) traveling to be with their NICU baby, not the baby being transferred. Key eligibility questions (medical stability, mobility confirmation) were pending when the session ended.
- (1x) Chatbot flagged for manual review because the specific seizure type was not confirmed, which is needed to evaluate medical stability for flight. All other criteria (location, distance, notice, mobility, financial need) appear to be met.
- (1x) Session is still in progress. Key details such as exact travel date and number of tickets (4 or 5) have not yet been confirmed. The chatbot had not reached a final eligibility determination before data extraction was requested.
- (1x) Patient meets core eligibility criteria (medical treatment, stable, mobile, financial need, sufficient notice, within service region), but the request for three companions exceeds the typical capacity for a volunteer pilot flight and requires coordinator review to determine if it can be accommodated.
- (1x) User is a caregiver traveling to support their father during chemotherapy. Trip is within service region, notice is sufficient, user is mobile and stable, and financial need is established via disability income. Chatbot determined the trip is eligible for the volunteer pilot program.
- (1x) Session was not completed. Financial need was not confirmed — user stated they can pay for Southwest Airlines. The chatbot agent asked for clarification but the session ended before a conclusion was reached.

## Session Rationale — Criterion fields cited on failures
- (20x) is_pregnant_rationale: No indication of pregnancy was mentioned in the conversation.
- (10x) dv_in_shelter_rationale: Not applicable — user confirmed this is not a domestic violence case.
- (10x) dv_provider_rationale: Not applicable — user confirmed this is not a domestic violence case.
- (7x) dv_in_shelter_rationale: Not applicable — this is not a DV case.
- (7x) dv_provider_rationale: Not applicable — this is not a DV case.
- (6x) dv_context_rationale: User explicitly stated "Not a domestic violence case."
- (5x) dv_in_shelter_rationale: Not applicable — user confirmed this is not a DV case.
- (5x) dv_provider_rationale: Not applicable — user confirmed this is not a DV case.
- (4x) is_pregnant_rationale: No mention of pregnancy in the conversation.
- (4x) dv_context_rationale: User explicitly stated "not a domestic violence case."
- (4x) dv_context_rationale: User explicitly stated this is not a domestic violence case.
- (3x) is_pregnant_rationale: No indication of pregnancy in the conversation.

## Rationale Evidence By Confusion Pattern
### truth `manual_review` → predicted `insufficient_information`
- F093: reason_codes: DATA_INCOMPLETE | outcome_notes: Screening was not completed. Key questions about mobility (unassisted boarding) and medical equipment needs (oxygen) were not fully resolved before the session ended. Financial need (Medicaid gaps) and route are favorable. Manual review or follow-up needed. | summary_notes: User is seeking travel from Tucson, AZ to Phoenix, AZ for medical treatment approximately 12 days out. User clarified this is not a domestic violence case. Mentioned Medicaid gaps as a financial need. A sister may travel as a companion. Passenger may need a hand on stairs but stated no nurse is needed. Questions about oxygen/medical equipment and companion were unanswered at extraction time.
- F093 @ q1: reason_codes: DATA_INCOMPLETE
- F100: reason_codes: DATA_INCOMPLETE, EDGE_CASE_COMPLEX | outcome_notes: Screening is still in progress. Key DV criteria (shelter status, documentation) are unconfirmed. Service dog size and companion logistics are unresolved, which may affect small-plane feasibility. Manual review likely needed once screening is complete. | summary_notes: User is a DV survivor seeking relocation from Reno, NV to Los Angeles, CA. Approximately 11 days of notice provided. User is mobile, medically stable, has no financial resources, and has a shelter advocate involved. Two companions and a service dog are traveling. Service dog size and shelter residency status are still unconfirmed. Conversation is still mid-screening.
- F100 @ q1: reason_codes: DATA_INCOMPLETE
### truth `ineligible` → predicted `insufficient_information`
- F015: reason_codes: DATA_INCOMPLETE | outcome_notes: The chatbot had not yet reached a final eligibility conclusion. Key missing information includes: confirmation of user role (patient vs. caregiver), exact travel date, and whether minimum notice requirements are met. The conversation ended mid-screening. | summary_notes: User is traveling from Honolulu, HI to San Francisco, CA for a specialist medical appointment. They mentioned traveling with one companion, no in-flight monitoring needed, no travel funds, and explicitly stated the trip is not DV-related. The exact Monday travel date was not confirmed. The chatbot was still gathering information when the extract was requested.
- F015 @ q1: reason_codes: DATA_INCOMPLETE
- F020: reason_codes: DATA_INCOMPLETE | outcome_notes: Screening was still in progress at the end of the conversation. The user clarified they are the caregiver (parent) traveling to be with their NICU baby, not the baby being transferred. Key eligibility questions (medical stability, mobility confirmation) were pending when the session ended. | summary_notes: User initially requested help with a NICU helicopter transfer from Reno, NV to Palo Alto, CA, which was declined as AFW does not provide air ambulance services. After further clarification, the user indicated they are a parent/caregiver traveling to be with their NICU baby. User confirmed mobility and mentioned Medicaid as financial context. Screening was still in progress with follow-up questions pending about medical stability and mobility on a small aircraft.
- F020 @ q1: reason_codes: REASON_FOR_TRAVEL_NOT_ELIGIBLE
### truth `eligible` → predicted `ineligible`
- F036: reason_codes: INSUFFICIENT_NOTICE | outcome_notes: Patient is traveling from Redding to Sacramento for a burn clinic follow-up. Meets mobility, medical stability, and financial need criteria. However, the appointment is only 3 days away, which does not meet the minimum 5-business-day notice requirement for the volunteer pilot pathway. User was referred to Air Care Alliance for shorter-notice options. | summary_notes: A patient on SSDI is seeking a flight from Redding, CA to Sacramento, CA for a burn clinic follow-up appointment. The user is independently mobile, does not require medical monitoring, and will travel solo. Financial need is established via SSDI. The only disqualifying factor is the 3-day notice — insufficient for the volunteer pilot program. User was referred to Air Care Alliance and encouraged to contact AFW for future appointments with more lead time.
- F036 @ q1: reason_codes: DATA_INCOMPLETE
- F037: reason_codes: INSUFFICIENT_NOTICE | outcome_notes: User is traveling from Stockton, CA to San Francisco, CA for an MFM medical appointment in 2 days. While the user meets mobility, medical stability, and financial need criteria, the trip does not meet the minimum notice requirement for volunteer pilot coordination. User was referred to Air Care Alliance for shorter-notice assistance. | summary_notes: User is requesting a flight from Stockton, CA to San Francisco, CA for a maternal-fetal medicine (MFM) appointment occurring in 2 days. User is mobile, medically stable, does not need in-flight monitoring, and is on a single income. Pregnancy status was not explicitly confirmed. The chatbot determined the trip is ineligible due to insufficient notice (2 days vs. required 5 business days). User was referred to Air Care Alliance.
- F037 @ q1: reason_codes: DATA_INCOMPLETE
### truth `insufficient_information` → predicted `manual_review`
- F066: reason_codes: DATA_INCOMPLETE | outcome_notes: User was unable or unwilling to provide key details (origin, destination, travel date) needed to complete screening. Chatbot referred the case to a coordinator for follow-up. | summary_notes: User initiated a conversation about travel assistance but provided very vague responses throughout. They indicated the travel was to see a doctor but could not or would not provide origin city/state, destination city/state, or travel date. The chatbot was unable to complete the eligibility screening and offered to connect the user with a coordinator.
- F070: reason_codes: DATA_INCOMPLETE | outcome_notes: Origin and destination are unknown; full eligibility screening could not be completed. Chatbot referred the case for manual coordinator review and asked the user for contact information. | summary_notes: User reached out with a potential domestic violence relocation request. They were vague throughout the conversation, unable to provide origin, destination, or travel date. The chatbot repeatedly asked for location details but received non-specific responses such as "Mountain area," "Pending," and "Unknown." The chatbot concluded the screening could not be completed and flagged the case for manual coordinator review.
- F070 @ q7: reason_codes: DATA_INCOMPLETE
- F072: reason_codes: DATA_INCOMPLETE | outcome_notes: User could not provide specific origin and destination city/state — locations reportedly vary weekly. Chatbot agent escalated to manual review for coordinator follow-up. DV context indicated but not confirmed. DV advocate involvement not established. | summary_notes: User reached out about potential travel assistance in what may be a domestic violence situation. When asked for origin and destination, the user indicated the locations vary weekly and no specific towns were provided. The chatbot agent was unable to assess service region, distance, travel pathway, or other eligibility criteria. The agent escalated to manual review and asked the user to provide contact details for coordinator follow-up. The agent also advised that a DV advocate would need to be involved.
### truth `manual_review` → predicted `ineligible`
- F104: reason_codes: DISTANCE_TOO_GREAT | outcome_notes: Trip from Mesa, AZ to Phoenix, AZ is too short (~20 miles) to qualify for Angel Flight West. Despite user meeting mobility, stability, and financial need criteria, the distance disqualifies the request. User was referred to Air Care Alliance for local transport assistance. | summary_notes: Patient is seeking transportation from Mesa, AZ to Phoenix, AZ for surgery. User clarified this is not a DV case. They are mobile, medically stable, travel solo, and report financial hardship. Clinic date is shifting 6–9 days out. The chatbot agent determined the trip is too short to qualify for AFW services and referred the user to Air Care Alliance.
- F104 @ q1: reason_codes: DISTANCE_TOO_GREAT
- F106: reason_codes: DISTANCE_TOO_GREAT | outcome_notes: Trip from Loveland, CO to Denver, CO is too short (~50 miles) for Angel Flight West to assist. AFW flights are designed for longer distances where ground travel is not practical. User was referred to Air Care Alliance and other local resources. | summary_notes: Patient is traveling from Loveland, CO to Denver, CO for chemotherapy treatment in approximately 9 days. User is mobile and medically stable, on a pension (fixed income), and explicitly noted this is not a DV case. The chatbot determined the trip is too short for AFW services and referred the user to alternative resources.
- F106 @ q1: reason_codes: DISTANCE_TOO_GREAT
### truth `ineligible` → predicted `manual_review`
- F018: reason_codes: DATA_INCOMPLETE, MOBILITY_CRITERIA_NOT_MET | outcome_notes: Screening is incomplete. Mobility status is unclear due to post-amputation non-weight-bearing condition. Medical stability during flight has not yet been confirmed. Coordinator follow-up needed. | summary_notes: User is requesting travel from Idaho Falls, ID to Boise, ID for a post-amputation follow-up appointment, approximately 9 days out. The user is non-weight-bearing. DV was ruled out. The chatbot flagged mobility for manual review and asked about in-flight medical needs, but the session ended before those questions were answered.
- F018 @ q1: reason_codes: DATA_INCOMPLETE, MOBILITY_CRITERIA_NOT_MET
- F021: reason_codes: DATA_INCOMPLETE | outcome_notes: Chatbot flagged for manual review because the specific seizure type was not confirmed, which is needed to evaluate medical stability for flight. All other criteria (location, distance, notice, mobility, financial need) appear to be met. | summary_notes: Patient is traveling from Bakersfield, CA to Los Angeles, CA for epilepsy monitoring unit admission, approximately 13 days out. Patient walks independently, has seizures most weeks, and may be accompanied by their mother. Patient confirmed this is not DV-related. Specific seizure type was not confirmed during screening, prompting manual review referral.
- F021 @ q1: reason_codes: DATA_INCOMPLETE

## Incorrect Personas (with session rationale)
### F015 — truth `ineligible` vs pred `insufficient_information`
- first divergence: q1 (truth `eligible`, pred `insufficient_information`)
- final: reason_codes: DATA_INCOMPLETE
- final: outcome_notes: The chatbot had not yet reached a final eligibility conclusion. Key missing information includes: confirmation of user role (patient vs. caregiver), exact travel date, and whether minimum notice requirements are met. The conversation ended mid-screening.
- final: summary_notes: User is traveling from Honolulu, HI to San Francisco, CA for a specialist medical appointment. They mentioned traveling with one companion, no in-flight monitoring needed, no travel funds, and explicitly stated the trip is not DV-related. The exact Monday travel date was not confirmed. The chatbot was still gathering information when the extract was requested.
- final: service_region_rationale: Both Hawaii (HI) and California (CA) are within Angel Flight West's service region.
- final: within_distance_limit_rationale: The distance from Honolulu, HI to San Francisco, CA is approximately 2,393 miles, which far exceeds the 900-mile limit for small-plane volunteer flights. This route would require commercial air travel.
- final: minimum_notice_rationale: The user mentioned travel on "Monday" but did not specify which Monday. It was not possible to confirm whether minimum notice requirements (2 business days for commercial) are met.
- final: requires_small_plane_rationale: The route from Honolulu to San Francisco (~2,393 miles) far exceeds the 900-mile small-plane limit, making volunteer pilot flight not feasible.
- final: requires_commercial_rationale: Given the over-ocean distance from Honolulu, HI to San Francisco, CA (~2,393 miles), commercial air travel (e.g., Alaska Airlines partner) is the only viable pathway.
- final: is_mobile_rationale: The user stated "ok on planes" and mentioned traveling with one companion, suggesting they are able to board and travel on a commercial flight.
- final: is_medically_stable_rationale: The user indicated "no monitoring" needed during travel, suggesting medical stability for non-emergency air travel.
- final: is_pregnant_rationale: No indication of pregnancy was mentioned in the conversation.
- final: summary_compelling_or_financial_need_notes: User stated they have no travel fund, indicating a clear financial hardship and inability to self-fund commercial travel to the mainland for a specialist appointment.
- final: summary_sentiment_analysis: The user appeared cooperative but provided brief, fragmented responses throughout the conversation. There were signs of mild frustration or impatience, particularly with repeated clarifying questions. Overall tone was neutral to slightly terse.
- at q1: reason_codes: DATA_INCOMPLETE

### F018 — truth `ineligible` vs pred `manual_review`
- first divergence: q1 (truth `eligible`, pred `insufficient_information`)
- final: reason_codes: DATA_INCOMPLETE, MOBILITY_CRITERIA_NOT_MET
- final: outcome_notes: Screening is incomplete. Mobility status is unclear due to post-amputation non-weight-bearing condition. Medical stability during flight has not yet been confirmed. Coordinator follow-up needed.
- final: summary_notes: User is requesting travel from Idaho Falls, ID to Boise, ID for a post-amputation follow-up appointment, approximately 9 days out. The user is non-weight-bearing. DV was ruled out. The chatbot flagged mobility for manual review and asked about in-flight medical needs, but the session ended before those questions were answered.
- final: service_region_rationale: Both Idaho Falls, ID and Boise, ID are within AFW's service region (Idaho is a served state).
- final: within_distance_limit_rationale: The approximate distance from Idaho Falls to Boise is approximately 220 miles, well within the 900-mile small-plane limit.
- final: minimum_notice_rationale: User indicated approximately 9 days until travel, which meets the minimum 5 business day notice requirement for volunteer pilot flights.
- final: requires_small_plane_rationale: The route from Idaho Falls to Boise is approximately 220 miles and within AFW's small-plane service area. No indication of commercial pathway needed.
- final: requires_commercial_rationale: Distance and route are appropriate for volunteer small-plane travel; no indication that commercial flight is needed.
- final: is_mobile_rationale: Passenger is post-amputation and non-weight-bearing. The chatbot flagged mobility for coordinator follow-up, as it was unclear whether the passenger could independently board a small aircraft. No definitive answer was provided by the user.
- final: is_medically_stable_rationale: The chatbot asked whether the passenger would need medical monitoring or care during the flight, but the conversation ended before a response was given.
- final: is_pregnant_rationale: No indication of pregnancy was mentioned in the conversation.
- final: summary_compelling_or_financial_need_notes: No financial or compelling need information was collected during this session.
- final: summary_sentiment_analysis: The user was brief and factual in their responses, providing relevant details without elaboration. No emotional distress was apparent, though responses were minimal and the session ended mid-screening.
- at q1: reason_codes: DATA_INCOMPLETE, MOBILITY_CRITERIA_NOT_MET

### F020 — truth `ineligible` vs pred `insufficient_information`
- first divergence: q1 (truth `eligible`, pred `ineligible`)
- final: reason_codes: DATA_INCOMPLETE
- final: outcome_notes: Screening was still in progress at the end of the conversation. The user clarified they are the caregiver (parent) traveling to be with their NICU baby, not the baby being transferred. Key eligibility questions (medical stability, mobility confirmation) were pending when the session ended.
- final: summary_notes: User initially requested help with a NICU helicopter transfer from Reno, NV to Palo Alto, CA, which was declined as AFW does not provide air ambulance services. After further clarification, the user indicated they are a parent/caregiver traveling to be with their NICU baby. User confirmed mobility and mentioned Medicaid as financial context. Screening was still in progress with follow-up questions pending about medical stability and mobility on a small aircraft.
- final: service_region_rationale: Both Reno, NV and Palo Alto, CA are within AFW's service region.
- final: within_distance_limit_rationale: Reno, NV to Palo Alto, CA is approximately 220 miles, well within the 900-mile small plane limit.
- final: minimum_notice_rationale: User indicated approximately 18 days until travel, which exceeds the 5 business day minimum notice for volunteer pilot flights.
- final: requires_small_plane_rationale: The route is approximately 220 miles and within the AFW service region, making it appropriate for a volunteer pilot small plane flight.
- final: requires_commercial_rationale: The distance and route are suitable for a small volunteer plane, so commercial is not anticipated.
- final: is_mobile_rationale: User stated "I am mobile" during the conversation, indicating they can board and travel on a small aircraft.
- final: is_medically_stable_rationale: Medical stability has not yet been confirmed by the chatbot agent — the screening was still in progress at the end of the conversation.
- final: is_pregnant_rationale: No indication of pregnancy was mentioned in the conversation.
- final: summary_compelling_or_financial_need_notes: User mentioned Medicaid, suggesting financial hardship and a compelling need for assistance with transportation costs.
- final: summary_sentiment_analysis: User appeared distressed and terse, likely due to the stress of having a baby in the NICU. Responses were brief and focused. There was some frustration when initial clarifications were needed, but the user was cooperative in providing additional information.
- at q1: reason_codes: REASON_FOR_TRAVEL_NOT_ELIGIBLE

### F021 — truth `ineligible` vs pred `manual_review`
- first divergence: q1 (truth `eligible`, pred `insufficient_information`)
- final: reason_codes: DATA_INCOMPLETE
- final: outcome_notes: Chatbot flagged for manual review because the specific seizure type was not confirmed, which is needed to evaluate medical stability for flight. All other criteria (location, distance, notice, mobility, financial need) appear to be met.
- final: summary_notes: Patient is traveling from Bakersfield, CA to Los Angeles, CA for epilepsy monitoring unit admission, approximately 13 days out. Patient walks independently, has seizures most weeks, and may be accompanied by their mother. Patient confirmed this is not DV-related. Specific seizure type was not confirmed during screening, prompting manual review referral.
- final: service_region_rationale: Both Bakersfield, CA and Los Angeles, CA are within California, which is within AFW's service region.
- final: within_distance_limit_rationale: The route from Bakersfield to Los Angeles is approximately 110 miles, well within the 900-mile limit for small-plane volunteer travel.
- final: minimum_notice_rationale: User stated travel is approximately 13 days out, which exceeds the 5 business day minimum notice requirement for volunteer pilot travel.
- final: requires_small_plane_rationale: The distance (~110 miles) and route between Bakersfield and Los Angeles are well-suited for volunteer small-plane travel.
- final: requires_commercial_rationale: The short distance and in-state route do not indicate a need for commercial air travel.
- final: is_mobile_rationale: User stated the passenger "walks alone," indicating they are independently mobile.
- final: is_medically_stable_rationale: Medical stability could not be fully confirmed. The chatbot noted that the specific seizure type was not confirmed, which is needed to evaluate medical stability for flight. User did mention seizures occur most weeks.
- final: is_pregnant_rationale: No indication of pregnancy was mentioned in the conversation.
- final: summary_compelling_or_financial_need_notes: User reported "little savings," indicating limited financial resources and a clear financial need for assistance with travel costs.
- final: summary_sentiment_analysis: User was cooperative and responsive but provided minimal detail throughout the conversation. Responses were brief and factual. No distress or urgency was expressed, though the medical context (frequent seizures, limited savings) suggests underlying stress.
- at q1: reason_codes: DATA_INCOMPLETE

### F024 — truth `ineligible` vs pred `insufficient_information`
- first divergence: q1 (truth `eligible`, pred `insufficient_information`)
- final: reason_codes: DATA_INCOMPLETE
- final: outcome_notes: Session is still in progress. Key details such as exact travel date and number of tickets (4 or 5) have not yet been confirmed. The chatbot had not reached a final eligibility determination before data extraction was requested.
- final: summary_notes: User is traveling from Anchorage, AK to Seattle, WA for ongoing chemotherapy treatment. Travel party includes at least a patient, spouse, and two children (ticket count of 4 or 5 is unresolved). User confirmed commercial airline seating is acceptable and patient is medically stable. Travel is approximately 10 days out. User cited high Alaska travel costs as a financial hardship. User confirmed this is not a DV case. Session was interrupted before final eligibility determination.
- final: service_region_rationale: Both Anchorage, AK and Seattle, WA are within AFW's service region (Alaska and Washington are covered states).
- final: within_distance_limit_rationale: The distance from Anchorage, AK to Seattle, WA is approximately 1,448 miles, which exceeds the 900-mile limit for small-plane volunteer travel. Commercial pathway (Alaska Airlines) would be applicable.
- final: minimum_notice_rationale: User indicated travel is approximately 10 days out, which meets the minimum notice requirement of 2 business days for commercial travel.
- final: requires_small_plane_rationale: Distance from Anchorage to Seattle (~1,448 miles) exceeds the small-plane volunteer limit of 900 miles, so small-plane travel is not applicable.
- final: requires_commercial_rationale: Due to the distance (~1,448 miles) and Alaska location, the commercial airline pathway (e.g., Alaska Airlines partnership) is the appropriate route.
- final: is_mobile_rationale: User confirmed that commercial/airline seating is acceptable ("Airline ok"), indicating the patient can sit upright and board/exit a standard aircraft.
- final: is_medically_stable_rationale: User stated the patient is "stable," indicating no need for in-flight medical monitoring or emergency care.
- final: is_pregnant_rationale: No indication of pregnancy in the conversation.
- final: summary_compelling_or_financial_need_notes: User referenced "Alaska costs" as a significant financial barrier, indicating difficulty affording commercial airline travel from Anchorage for continued cancer treatment.
- final: summary_sentiment_analysis: User appeared cooperative and straightforward, providing brief but responsive answers. Mention of cancer treatment and family travel burden suggests emotional stress, though tone remained calm and factual throughout.
- at q1: reason_codes: DATA_INCOMPLETE

### F025 — truth `ineligible` vs pred `manual_review`
- first divergence: q1 (truth `eligible`, pred `insufficient_information`)
- final: reason_codes: EDGE_CASE_COMPLEX
- final: outcome_notes: Patient meets core eligibility criteria (medical treatment, stable, mobile, financial need, sufficient notice, within service region), but the request for three companions exceeds the typical capacity for a volunteer pilot flight and requires coordinator review to determine if it can be accommodated.
- final: summary_notes: User is requesting travel for a patient from Fresno, CA to Los Angeles, CA for radiation treatment. The patient walks unassisted and is medically stable. The user reported they cannot afford commercial or car travel. The trip involves 3 companions, which is above the standard volunteer pilot capacity and was flagged for manual coordinator review. 14 days notice was given.
- final: service_region_rationale: Both Fresno, CA and Los Angeles, CA are within California, which is within AFW's service region.
- final: within_distance_limit_rationale: The distance from Fresno to Los Angeles is approximately 220 miles, well within the 900-mile limit for small plane travel.
- final: minimum_notice_rationale: User stated 14 days notice, which exceeds the 5 business day minimum for volunteer pilot flights.
- final: requires_small_plane_rationale: The route is within California at approximately 220 miles, making it appropriate for a volunteer small-plane flight.
- final: requires_commercial_rationale: Distance and route are well within the volunteer pilot range; no indicators for commercial pathway were identified.
- final: is_mobile_rationale: User stated the patient "walks fine," indicating the patient can board and move independently.
- final: is_medically_stable_rationale: User stated the patient is "stable," indicating the patient is medically stable for non-emergency air travel and does not require in-flight medical care.
- final: is_pregnant_rationale: No indication of pregnancy was mentioned in the conversation.
- final: summary_compelling_or_financial_need_notes: User stated they "can't pay," indicating a clear financial hardship that makes commercial transportation inaccessible.
- final: summary_sentiment_analysis: The user was brief and cooperative throughout the conversation. Responses were minimal but direct. No signs of distress were evident, though the financial hardship suggests a stressful situation. The user appeared motivated to find a solution.
- at q1: reason_codes: DATA_INCOMPLETE

### F026 — truth `ineligible` vs pred `eligible`
- first divergence: q1 (truth `eligible`, pred `insufficient_information`)
- final: reason_codes: OTHER
- final: outcome_notes: User is a caregiver traveling to support their father during chemotherapy. Trip is within service region, notice is sufficient, user is mobile and stable, and financial need is established via disability income. Chatbot determined the trip is eligible for the volunteer pilot program.
- final: summary_notes: User is a caregiver (not a patient) traveling from Modesto, CA to San Francisco, CA to support their father undergoing chemotherapy. Travel is approximately 11 days away. User confirmed mobility and medical stability, is not a DV case, and reports disability income as a financial need. Chatbot determined eligibility for the volunteer pilot program and provided an application link.
- final: service_region_rationale: Both Modesto, CA and San Francisco, CA are within Angel Flight West's service region (California is a covered state).
- final: within_distance_limit_rationale: Modesto to San Francisco is approximately 90 miles one-way, well within the 900-mile small-plane limit.
- final: minimum_notice_rationale: User indicated travel is approximately 11 days away, which exceeds the 5 business day minimum notice requirement for volunteer pilot flights.
- final: requires_small_plane_rationale: The chatbot determined the trip is eligible for the volunteer pilot program, and the short distance (~90 miles) between Modesto and San Francisco is well-suited for a small volunteer aircraft.
- final: requires_commercial_rationale: The route and circumstances do not indicate a need for commercial airline travel; the chatbot directed the user to the volunteer pilot program.
- final: is_mobile_rationale: User confirmed they are mobile and can board a small aircraft unassisted when asked about mobility.
- final: is_medically_stable_rationale: User confirmed they are medically stable and will not require medical care, monitoring, or oxygen during the flight.
- final: is_pregnant_rationale: No indication of pregnancy was mentioned in the conversation.
- final: summary_compelling_or_financial_need_notes: User is on disability income, indicating limited financial resources and an inability to easily cover commercial transportation costs for a recurring caregiver role.
- final: summary_sentiment_analysis: User was brief and direct throughout the conversation, providing terse but clear responses. Tone was cooperative and focused. No signs of distress or frustration, though the user appeared unfamiliar with how to describe their situation (e.g., clarifying they are the caregiver, not the patient, multiple times).
- at q1: reason_codes: DATA_INCOMPLETE

### F027 — truth `ineligible` vs pred `insufficient_information`
- first divergence: q1 (truth `eligible`, pred `insufficient_information`)
- final: reason_codes: DATA_INCOMPLETE, FINANCIAL_CRITERIA_NOT_MET
- final: outcome_notes: Session was not completed. Financial need was not confirmed — user stated they can pay for Southwest Airlines. The chatbot agent asked for clarification but the session ended before a conclusion was reached.
- final: summary_notes: Patient is seeking travel assistance from San Jose, CA to Sacramento, CA (~90 miles) for a cardiology follow-up appointment approximately 9 days away. User is traveling solo, is mobile, and medically stable. User explicitly ruled out DV context. User mentioned being able to pay for Southwest Airlines, raising a question about financial eligibility. The chatbot was in the process of clarifying financial need when the session ended.
- final: service_region_rationale: Both San Jose, CA and Sacramento, CA are within California, which is within AFW's service region.
- final: within_distance_limit_rationale: San Jose to Sacramento is approximately 90 miles, well within the 900-mile small plane limit.
- final: minimum_notice_rationale: User indicated approximately 9 days until travel, which meets the minimum 5 business days notice requirement for volunteer pilot flights.
- final: requires_small_plane_rationale: The route is approximately 90 miles, which is well within volunteer small-plane range. The user is traveling solo and the destination is within California.
- final: requires_commercial_rationale: The route is short and does not require commercial airline travel. The user mentioned Southwest but no commercial pathway was determined by the agent.
- final: is_mobile_rationale: User responded "Fine" when asked about ability to step into aircraft, move in and out of seat, and sit upright with seatbelt.
- final: is_medically_stable_rationale: User responded "Stable" when asked about need for medical monitoring, nursing care, or equipment during flight.
- final: is_pregnant_rationale: No indication of pregnancy was mentioned in the conversation.
- final: summary_compelling_or_financial_need_notes: User stated "we can pay for Southwest," which suggests possible financial ability to afford commercial travel. Financial hardship or compelling transportation need was not confirmed before the session ended.
- final: summary_sentiment_analysis: User was cooperative but brief in responses, providing minimal information. The mention of being able to pay for Southwest may indicate some uncertainty about eligibility or a misunderstanding of the program. Tone was neutral and matter-of-fact.
- at q1: reason_codes: DATA_INCOMPLETE

### F028 — truth `ineligible` vs pred `insufficient_information`
- first divergence: q1 (truth `eligible`, pred `insufficient_information`)
- final: reason_codes: DATA_INCOMPLETE, FINANCIAL_CRITERIA_NOT_MET
- final: outcome_notes: Screening was not completed. The session was still in progress — the chatbot was awaiting answers about pets/service animals, and the financial need criterion has not been confirmed. The user indicated insurance may cover transport, which raises a question about financial/compelling need eligibility.
- final: summary_notes: User is requesting a flight from Oakland, CA to Portland, OR for an orthopedic consultation approximately 13 days away. The passenger is traveling alone, is mobile, and does not require medical monitoring during the flight. The user mentioned insurance covers transport. The session was not completed — the chatbot was still asking about pets/service animals when data extraction was requested.
- final: service_region_rationale: Both Oakland, CA and Portland, OR are within AFW's service region (CA and OR are both covered states).
- final: within_distance_limit_rationale: The approximate distance from Oakland, CA to Portland, OR is roughly 550 miles, which is within the 900-mile limit for small-plane travel.
- final: minimum_notice_rationale: The user stated travel is needed in approximately 13 days, which meets the minimum 5 business days' notice required for volunteer pilot travel.
- final: requires_small_plane_rationale: The route (Oakland to Portland, ~550 miles) is within small-plane range and the passenger reports being mobile and not requiring medical monitoring, making volunteer small-plane travel appropriate.
- final: requires_commercial_rationale: No indication that commercial travel is needed. The passenger is mobile and medically stable, and the route is within small-plane range.
- final: is_mobile_rationale: The user confirmed the passenger has "ok mobility" and can manage boarding a small aircraft independently.
- final: is_medically_stable_rationale: The user confirmed no monitoring or medical equipment is needed during the flight, indicating the passenger is medically stable for non-emergency air travel.
- final: is_pregnant_rationale: No indication of pregnancy was mentioned in the conversation.
- final: summary_compelling_or_financial_need_notes: The user mentioned that insurance covers transport, which may indicate the passenger has existing transportation coverage and may not meet AFW's financial or compelling need criteria. This was not fully assessed by the chatbot.
- final: summary_sentiment_analysis: The user was cooperative and concise, providing brief but direct answers. The mention of insurance coverage suggests the user may be exploring multiple options. No signs of distress or urgency were noted.
- at q1: reason_codes: DATA_INCOMPLETE

### F029 — truth `ineligible` vs pred `insufficient_information`
- first divergence: q1 (truth `eligible`, pred `insufficient_information`)
- final: reason_codes: FINANCIAL_CRITERIA_NOT_MET, DATA_INCOMPLETE
- final: outcome_notes: Passenger is mobile, medically stable, and the route is within service region and distance limits. However, the user has explicitly stated no financial hardship and has savings. The chatbot was still exploring whether a compelling transportation need exists at the time of extraction. Eligibility cannot be confirmed without resolving the financial/compelling need criterion.
- final: summary_notes: User is requesting travel from Spokane, WA to Seattle, WA for an endocrine appointment approximately 12 days out. The passenger is mobile and medically stable. The user confirmed they have savings and no financial hardship. The chatbot was in the process of determining whether a compelling transportation need exists when the extraction was requested. DV context was explicitly ruled out by the user.
- final: service_region_rationale: Both Spokane, WA and Seattle, WA are within Angel Flight West's service region (Washington state is a covered state).
- final: within_distance_limit_rationale: Spokane to Seattle is approximately 280 miles, well within the 900-mile limit for volunteer small-plane travel.
- final: minimum_notice_rationale: The user indicated approximately 12 days until travel, which exceeds the 5 business day minimum notice requirement for volunteer pilot flights.
- final: requires_small_plane_rationale: The distance (~280 miles) and route are appropriate for a volunteer small-plane flight. No indication of commercial pathway was needed.
- final: requires_commercial_rationale: No indication that commercial travel is required; the route and distance are suitable for a volunteer pilot flight.
- final: is_mobile_rationale: The user confirmed the passenger is mobile and able to travel independently.
- final: is_medically_stable_rationale: The user confirmed the passenger is medically stable and does not require medical care or monitoring during the flight.
- final: is_pregnant_rationale: No mention of pregnancy in the conversation.
- final: summary_compelling_or_financial_need_notes: User explicitly stated they have savings and no financial hardship. No compelling transportation need had been confirmed at the time of extraction. The chatbot was still exploring this criterion.
- final: summary_sentiment_analysis: The user was cooperative but brief and somewhat terse in their responses. They were straightforward in providing information, including proactively ruling out DV context and clarifying their financial situation. No signs of distress or frustration were evident.
- at q1: reason_codes: DATA_INCOMPLETE, FINANCIAL_CRITERIA_NOT_MET

### F034 — truth `eligible` vs pred `insufficient_information`
- first divergence: q1 (truth `eligible`, pred `insufficient_information`)
- final: reason_codes: DATA_INCOMPLETE
- final: outcome_notes: Screening is still in progress. Key eligibility indicators are positive (mobile, medically stable, within service region, sufficient notice, rural barrier compelling need), but the session had not yet reached a conclusion — the chatbot was still asking about service animals/pets when data extraction was requested.
- final: summary_notes: Patient is traveling solo from Boise, ID to Salt Lake City, UT for an orthopedic follow-up appointment in approximately 12 days. They cited a rural barrier as their transportation need. They are mobile, do not require in-flight medical monitoring, will travel alone, and confirmed this is not a DV case. The session was interrupted before completion — the chatbot was asking about service animals when extraction was requested.
- final: service_region_rationale: Both Boise, ID and Salt Lake City, UT are within AFW's service region, which covers western US states including Idaho and Utah.
- final: within_distance_limit_rationale: The approximate distance between Boise, ID and Salt Lake City, UT is approximately 340 miles, well within the 900-mile small plane limit.
- final: minimum_notice_rationale: User indicated the appointment is in 12 days, which meets the minimum 5 business day notice requirement for the volunteer pilot pathway.
- final: requires_small_plane_rationale: The route is approximately 340 miles, within small plane range, and the user is mobile and does not require medical monitoring, making volunteer small-plane travel appropriate.
- final: requires_commercial_rationale: The distance and route do not require commercial travel; the volunteer small plane pathway appears suitable.
- final: is_mobile_rationale: User stated "I can walk and get around on my own," indicating sufficient mobility for small plane travel.
- final: is_medically_stable_rationale: User stated they do not need medical monitoring on the flight, indicating medical stability for non-emergency air travel.
- final: is_pregnant_rationale: No indication of pregnancy was mentioned in the conversation.
- final: summary_compelling_or_financial_need_notes: User cited "rural barrier" as their reason for needing assistance, indicating a compelling transportation need due to geographic isolation and limited access to orthopedic specialty care.
- final: summary_sentiment_analysis: The user was brief and task-focused, providing concise answers. They were cooperative and clarified unprompted that the trip was not DV-related. Tone appeared calm and straightforward, with no signs of distress.
- at q1: reason_codes: DATA_INCOMPLETE

### F036 — truth `eligible` vs pred `ineligible`
- first divergence: q1 (truth `eligible`, pred `insufficient_information`)
- final: reason_codes: INSUFFICIENT_NOTICE
- final: outcome_notes: Patient is traveling from Redding to Sacramento for a burn clinic follow-up. Meets mobility, medical stability, and financial need criteria. However, the appointment is only 3 days away, which does not meet the minimum 5-business-day notice requirement for the volunteer pilot pathway. User was referred to Air Care Alliance for shorter-notice options.
- final: summary_notes: A patient on SSDI is seeking a flight from Redding, CA to Sacramento, CA for a burn clinic follow-up appointment. The user is independently mobile, does not require medical monitoring, and will travel solo. Financial need is established via SSDI. The only disqualifying factor is the 3-day notice — insufficient for the volunteer pilot program. User was referred to Air Care Alliance and encouraged to contact AFW for future appointments with more lead time.
- final: service_region_rationale: Both Redding, CA and Sacramento, CA are within California, which is within AFW's service region.
- final: within_distance_limit_rationale: Redding to Sacramento is approximately 162 miles, well within the 900-mile small-plane limit.
- final: minimum_notice_rationale: The user stated the appointment is in 3 days. The volunteer pilot pathway requires a minimum of 5 business days notice, which is not met here. The chatbot explicitly identified the 3-day timeline as the disqualifying factor.
- final: requires_small_plane_rationale: The route (Redding to Sacramento, ~162 miles) is appropriate for a volunteer small-plane flight. The user stated they can walk and get around on their own, travel solo, and do not need medical monitoring.
- final: requires_commercial_rationale: The route is short and well within small-plane range; no indication that commercial travel was considered or required.
- final: is_mobile_rationale: The user explicitly stated "I can walk and get around on my own" and noted they would be traveling solo with no need for medical monitoring.
- final: is_medically_stable_rationale: The user stated they do not need medical monitoring on the flight and can get around on their own, indicating medical stability for non-emergency air travel.
- final: is_pregnant_rationale: No indication of pregnancy was mentioned in the conversation.
- final: summary_compelling_or_financial_need_notes: User is on SSDI, which the chatbot acknowledged as a real financial need. Burn clinic follow-up care is a compelling medical need. Both factors would support eligibility if notice requirements were met.
- final: summary_sentiment_analysis: The user was persistent and cooperative, offering clarifying information about their mobility, lack of need for medical monitoring, and solo travel status — likely hoping one of those factors could resolve the eligibility issue. Their tone was matter-of-fact but may reflect some frustration or urgency given the short timeline and medical need.
- at q1: reason_codes: DATA_INCOMPLETE

