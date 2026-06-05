# Failure Analysis

## Run Summary
- personas: 120
- scored final outcomes: 120
- final outcome accuracy: 65.0%
- incorrect matches: 42
- unscored final outcomes: 0

## Error Concentration By Truth Class
- manual_review: 18 mismatches
- ineligible: 9 mismatches
- eligible: 8 mismatches
- insufficient_information: 7 mismatches

## Confusion Pairs
- truth `manual_review` predicted `insufficient_information`: 10
- truth `insufficient_information` predicted `manual_review`: 7
- truth `ineligible` predicted `insufficient_information`: 4
- truth `eligible` predicted `ineligible`: 4
- truth `manual_review` predicted `ineligible`: 4
- truth `manual_review` predicted `eligible`: 4
- truth `ineligible` predicted `manual_review`: 3
- truth `eligible` predicted `insufficient_information`: 3
- truth `ineligible` predicted `eligible`: 2
- truth `eligible` predicted `manual_review`: 1

## First Divergence Checkpoint
- q7: 37 mismatches
- q8: 37 mismatches
- q6: 36 mismatches
- q1: 35 mismatches
- q2: 35 mismatches
- q3: 35 mismatches
- q4: 35 mismatches
- q5: 35 mismatches

## Session Rationale — Outcome Reason Codes (failures only)
- `DATA_INCOMPLETE`: 17
- `OTHER`: 6
- `DISTANCE_TOO_GREAT`: 5
- `DATA_INCOMPLETE, MOBILITY_CRITERIA_NOT_MET`: 4
- `DATA_INCOMPLETE, FINANCIAL_CRITERIA_NOT_MET`: 3
- `INSUFFICIENT_NOTICE`: 3
- `MOBILITY_CRITERIA_NOT_MET`: 2
- `EDGE_CASE_COMPLEX`: 1
- `DATA_INCOMPLETE, MOBILITY_CRITERIA_NOT_MET, EDGE_CASE_COMPLEX`: 1

## Session Rationale — Final outcome_notes (failures only)
- (1x) Session was still in progress at the time of extraction. Travel date was vague ("Monday"), exact notice days could not be confirmed, and the conversation had not yet reached a final eligibility determination. Commercial pathway likely given HI-CA route.
- (1x) Screening incomplete — financial need question was not answered. Additionally, the passenger requires a lift to board, which raises a mobility concern for the small-plane volunteer pathway. Manual review recommended once financial need is confirmed.
- (1x) Passenger is non-weight bearing post-amputation and cannot meet the mobility requirement for volunteer pilot flights. Chatbot offered manual coordinator review or referral to Air Care Alliance. Session ended without a final resolution from the user.
- (1x) The session began as a NICU helicopter transfer request (ineligible), but shifted to a caregiver-only trip at the end. The chatbot had not yet completed screening for the caregiver-only trip — key details such as reason for travel, medical stability, and travel date are still missing. Session ended mid-screening.
- (1x) Screening was not completed. The chatbot agent was still gathering information about seizure type to assess medical stability when the conversation ended. All other criteria checked so far (location, distance, notice, mobility, financial need) appear favorable.
- (1x) Passenger is traveling for radiation treatment in LA from Fresno with three companions. All core eligibility criteria appear met (mobile, stable, financial need, within service region and distance), but the number of companions (3) exceeds the typical capacity for volunteer flights. Case sent for manual coordinator review.
- (1x) Caregiver traveling to support father undergoing chemotherapy in San Francisco from Modesto. User is mobile, medically stable, on disability income (financial need confirmed), and travel is 11 days out. Chatbot determined eligible for volunteer pilot program. Coordinator will verify with medical provider.
- (1x) Patient traveling solo from San Jose to Sacramento for a cardiology follow-up. Meets mobility, medical stability, notice, and service region criteria. Chatbot presented volunteer pilot pathway and provided application link. User later mentioned ability to pay for Southwest — coordinator should follow up on financial need and appropriate pathway.

## Session Rationale — Criterion fields cited on failures
- (19x) is_pregnant_rationale: No indication of pregnancy was mentioned in the conversation.
- (11x) dv_in_shelter_rationale: Not applicable — user confirmed this is not a domestic violence case.
- (11x) dv_provider_rationale: Not applicable — user confirmed this is not a domestic violence case.
- (8x) is_pregnant_rationale: No indication of pregnancy in the conversation.
- (7x) dv_context_rationale: User explicitly stated "Not a domestic violence case."
- (6x) dv_context_rationale: User explicitly stated this is not a domestic violence case.
- (5x) financial_need_rationale: Financial need was not discussed during the conversation.
- (4x) dv_in_shelter_rationale: Not applicable — user confirmed this is not a DV case.
- (4x) dv_provider_rationale: Not applicable — user confirmed this is not a DV case.
- (4x) dv_in_shelter_rationale: Not applicable — this is not a DV case.
- (4x) dv_provider_rationale: Not applicable — this is not a DV case.
- (4x) dv_context_rationale: The user explicitly stated this is not a domestic violence case.

## Rationale Evidence By Confusion Pattern
### truth `manual_review` → predicted `insufficient_information`
- F091: reason_codes: DATA_INCOMPLETE, MOBILITY_CRITERIA_NOT_MET | outcome_notes: Screening session was incomplete. Key details still needed include: mobility assessment (wheelchair user, may need step assistance), presence of service animal or pet, financial need, and exact travel date. Medically stable, route and timing are within AFW parameters. | summary_notes: User is a patient traveling from Sacramento, CA to Los Angeles, CA for medical treatment approximately 10 days from now. They will be accompanied by a partner. User uses a wheelchair and may need help with one step. They stated they are medically stable and do not require monitoring. User explicitly noted this is not a DV case. Session was still in progress when extraction was requested — questions about service animal/pet and financial need had not yet been answered.
- F091 @ q1: reason_codes: DATA_INCOMPLETE
- F093: reason_codes: DATA_INCOMPLETE, MOBILITY_CRITERIA_NOT_MET | outcome_notes: Conversation was still in progress at time of extraction. Mobility status is unclear (may need assistance boarding). Medical stability not yet confirmed — chatbot was still asking about supplemental oxygen. Financial need indicated via Medicaid gaps. Route and notice period appear to meet eligibility criteria. | summary_notes: User is seeking travel from Tucson, AZ to Phoenix, AZ for medical treatment approximately 12 days out. They clarified it is not a DV case. Mobility is uncertain — user said passenger is "usually ok" but may need a hand on stairs. No nurse needed. User mentioned Medicaid gaps as financial context. A sister may travel as companion. Chatbot was still screening for medical equipment needs (e.g., oxygen) when extraction was requested.
- F093 @ q1: reason_codes: DATA_INCOMPLETE
### truth `insufficient_information` → predicted `manual_review`
- F066: reason_codes: DATA_INCOMPLETE | outcome_notes: User was unable or unwilling to provide basic travel details (origin, destination, travel date). The chatbot was unable to complete the eligibility screening. Case escalated to a human coordinator for follow-up. | summary_notes: User initiated a chat requesting help with travel, possibly for a medical appointment. When asked for origin/destination cities and states, the user gave vague, non-committal responses ("Not sure," "Maybe," "Depends," "Probably fine"). Travel date was also unknown. The chatbot was unable to gather sufficient information to conduct a screening and escalated the case to a human coordinator.
- F068: reason_codes: DATA_INCOMPLETE | outcome_notes: User was unable or unwilling to provide origin and destination locations. Without this critical information, service region, distance, pathway, and notice requirements could not be assessed. Chatbot referred the case to a coordinator for follow-up. | summary_notes: User initiated a request for a flight for a health-related appointment. When asked for origin and destination cities and states, the user repeatedly deflected with responses like "Skip," "Between two cities," and "TBD." The user also mentioned uncertainty about "inflight care." The chatbot was unable to complete the eligibility screening due to missing location data and escalated to a coordinator.
- F069: reason_codes: DATA_INCOMPLETE | outcome_notes: User was unable or unwilling to provide sufficient details about the reason for travel, origin, destination, or travel date. Chatbot escalated to coordinator follow-up. | summary_notes: User was referred to the chatbot but could not articulate the reason for travel. Responses were vague ("N/a", "varies", "no details"). The chatbot attempted multiple rephrasing of the travel purpose question but could not gather enough information to proceed with screening. The session ended with the chatbot requesting contact details for coordinator follow-up.
- F070: reason_codes: DATA_INCOMPLETE | outcome_notes: User was unable to provide origin, destination, or travel date. The chatbot was unable to complete the eligibility screening and referred the case to a coordinator for follow-up. | summary_notes: User initiated a conversation after seeing the Angel Flight West website, expressing uncertainty about whether domestic violence relocation applied to their situation. They mentioned a "Mountain area" as a general location but could not provide specific origin or destination cities/states, or a travel date. The chatbot was unable to complete screening and directed the user to share contact information for coordinator follow-up.
### truth `ineligible` → predicted `insufficient_information`
- F015: reason_codes: DATA_INCOMPLETE | outcome_notes: Session was still in progress at the time of extraction. Travel date was vague ("Monday"), exact notice days could not be confirmed, and the conversation had not yet reached a final eligibility determination. Commercial pathway likely given HI-CA route. | summary_notes: Passenger is traveling from Honolulu, HI to San Francisco, CA to see a mainland specialist. Travel is requested for "Monday." Passenger is mobile, medically stable (no in-flight monitoring needed), and will have one companion. No prior Angel Flight West travel this year. User indicated no travel funds available. DV context was explicitly ruled out. Session ended mid-screening with a question about pets/service animals still pending.
- F015 @ q1: reason_codes: DATA_INCOMPLETE
- F020: reason_codes: DATA_INCOMPLETE | outcome_notes: The session began as a NICU helicopter transfer request (ineligible), but shifted to a caregiver-only trip at the end. The chatbot had not yet completed screening for the caregiver-only trip — key details such as reason for travel, medical stability, and travel date are still missing. Session ended mid-screening. | summary_notes: The user initially requested help with a NICU helicopter transfer from Reno, NV to Palo Alto, CA. The chatbot correctly identified this as an air ambulance request outside AFW's scope and referred the user to the Air Care Alliance. The user then clarified they wanted to travel alone (without the baby) and mentioned Medicaid as context for financial need. The chatbot was in the process of clarifying the purpose of the caregiver-only trip when the session ended.
- F020 @ q1: reason_codes: REASON_FOR_TRAVEL_NOT_ELIGIBLE
### truth `eligible` → predicted `ineligible`
- F036: reason_codes: INSUFFICIENT_NOTICE | outcome_notes: Patient is otherwise a strong candidate (medical need, financial need via SSDI, mobile, medically stable, within service region), but the appointment is only 3 days away, which does not meet the 5 business day minimum notice requirement for volunteer pilot flights. | summary_notes: Patient is traveling from Redding, CA to Sacramento, CA for a burn clinic follow-up appointment. They are on SSDI, mobile, traveling solo, and do not require medical monitoring. The only barrier is insufficient notice — the appointment is 3 days away, and volunteer flights require at least 5 business days of lead time. The chatbot referred the user to Air Care Alliance for shorter-notice options.
- F036 @ q1: reason_codes: DATA_INCOMPLETE
- F037: reason_codes: INSUFFICIENT_NOTICE | outcome_notes: Patient is traveling from Stockton, CA to San Francisco, CA for a medical (MFM) appointment. They are mobile, medically stable, and have a financial need (single income). However, the trip is only 2 days away, which does not meet the 5 business day minimum notice requirement for volunteer pilot flights. Case was deemed ineligible due to insufficient notice. | summary_notes: User is a patient traveling from Stockton, CA to San Francisco, CA for an MFM (Maternal-Fetal Medicine) appointment in 2 days. They are self-ambulatory, do not need in-flight medical monitoring, and are on a single income. The spouse may accompany them. The case was ruled ineligible solely due to insufficient advance notice (2 days vs. required 5 business days). The chatbot referred the user to Air Care Alliance for short-notice options.
- F037 @ q1: reason_codes: DATA_INCOMPLETE
### truth `manual_review` → predicted `ineligible`
- F104: reason_codes: DISTANCE_TOO_GREAT | outcome_notes: Trip from Mesa, AZ to Phoenix, AZ is too short (~20 miles) for Angel Flight West. All other criteria (mobility, medical stability, financial need) were met, but distance is the disqualifying factor. User was referred to Air Care Alliance and local resources. | summary_notes: Patient needs transportation from Mesa, AZ to Phoenix, AZ for surgery. User confirmed they are mobile (walks and transfers without help), medically stable, traveling solo, and facing financial hardship. The trip is not a DV case. The chatbot agent determined the trip is ineligible solely due to insufficient distance. User was referred to Air Care Alliance, hospital social work, and 2-1-1.
- F104 @ q1: reason_codes: DISTANCE_TOO_GREAT
- F108: reason_codes: MOBILITY_CRITERIA_NOT_MET | outcome_notes: Passenger is 5 months pregnant with a high-risk pregnancy. AFW policy does not permit flights for high-risk pregnancies due to in-flight safety considerations. All other criteria (route, distance, notice, mobility, financial need) appear to be met. User was referred to Air Care Alliance. | summary_notes: User is a patient seeking a flight from Klamath Falls, OR to Portland, OR for a high-risk pregnancy at 5 months (described as borderline). Travel is approximately 12 days away. User is mobile and independent, on a single income, and traveling with a partner. The case is not DV-related. The chatbot determined ineligibility solely due to the high-risk pregnancy policy restriction and referred the user to Air Care Alliance.
- F108 @ q1: reason_codes: MOBILITY_CRITERIA_NOT_MET
### truth `manual_review` → predicted `eligible`
- F105: reason_codes: OTHER | outcome_notes: Patient traveling from Grants Pass, OR to Portland, OR for infusion treatment. Medically stable, mobile, has disability creating compelling transportation need. Chatbot agent determined eligible for volunteer pilot pathway. | summary_notes: Patient needs a flight from Grants Pass, OR to Portland, OR for infusion treatment, likely next month (no fixed date yet). They travel alone, are mobile and medically stable, and cited disability as a barrier to independent travel. Chatbot agent determined eligibility for volunteer pilot pathway and directed user to the online application.
- F105 @ q1: reason_codes: DATA_INCOMPLETE
- F106: reason_codes: OTHER | outcome_notes: Patient traveling from Loveland, CO to Denver, CO for chemotherapy. Medically stable, mobile, on a pension (financial need indicated), travel is ~9 days out. Chatbot determined eligible for volunteer pilot program and directed user to complete an application. | summary_notes: Patient is seeking a flight from Loveland, CO to Denver, CO for chemotherapy treatment approximately 9 days from now. User confirmed they are mobile and medically stable. They clarified the case is not related to domestic violence. When asked about financial hardship, user mentioned being on a pension. Chatbot concluded the trip is eligible for the volunteer pilot program and directed user to complete an online flight application.
- F106 @ q1: reason_codes: DATA_INCOMPLETE

## Incorrect Personas (with session rationale)
### F015 — truth `ineligible` vs pred `insufficient_information`
- first divergence: q1 (truth `eligible`, pred `insufficient_information`)
- final: reason_codes: DATA_INCOMPLETE
- final: outcome_notes: Session was still in progress at the time of extraction. Travel date was vague ("Monday"), exact notice days could not be confirmed, and the conversation had not yet reached a final eligibility determination. Commercial pathway likely given HI-CA route.
- final: summary_notes: Passenger is traveling from Honolulu, HI to San Francisco, CA to see a mainland specialist. Travel is requested for "Monday." Passenger is mobile, medically stable (no in-flight monitoring needed), and will have one companion. No prior Angel Flight West travel this year. User indicated no travel funds available. DV context was explicitly ruled out. Session ended mid-screening with a question about pets/service animals still pending.
- final: service_region_rationale: Hawaii (HI) is within AFW's service region. The destination, San Francisco, CA, is also within AFW's service region.
- final: within_distance_limit_rationale: Honolulu, HI to San Francisco, CA is approximately 2,393 miles one-way, far exceeding the 900-mile small-plane limit. Commercial pathway would be required.
- final: minimum_notice_rationale: User mentioned travel on "Monday" but no specific date was provided, so the exact number of days until travel and minimum notice cannot be confirmed.
- final: requires_small_plane_rationale: Distance of ~2,393 miles far exceeds the small-plane range. A transoceanic route from Hawaii to the mainland is not feasible for a volunteer small plane.
- final: requires_commercial_rationale: Hawaii to California requires commercial air travel due to the overwater transoceanic distance (~2,393 miles). This would fall under the Alaska Airlines/commercial partner pathway.
- final: is_mobile_rationale: User stated the passenger is "ok on planes," indicating ability to board and sit in a standard airline seat without special assistance.
- final: is_medically_stable_rationale: User confirmed no in-flight medical monitoring, nursing care, or medical equipment such as oxygen is needed.
- final: is_pregnant_rationale: No indication of pregnancy was mentioned in the conversation.
- final: summary_compelling_or_financial_need_notes: User stated "no travel fund," indicating financial hardship. Traveling from Hawaii to a mainland specialist represents a compelling medical transportation need that is cost-prohibitive without assistance.
- final: summary_sentiment_analysis: User was cooperative and responsive, providing brief but clear answers. Tone was calm and matter-of-fact. No signs of distress or frustration. The session appeared to be progressing normally before extraction was requested.
- at q1: reason_codes: DATA_INCOMPLETE

### F016 — truth `ineligible` vs pred `manual_review`
- first divergence: q1 (truth `eligible`, pred `insufficient_information`)
- final: reason_codes: DATA_INCOMPLETE, MOBILITY_CRITERIA_NOT_MET
- final: outcome_notes: Screening incomplete — financial need question was not answered. Additionally, the passenger requires a lift to board, which raises a mobility concern for the small-plane volunteer pathway. Manual review recommended once financial need is confirmed.
- final: summary_notes: User is requesting travel from Wenatchee, WA to Spokane, WA for dialysis/access care. Approximately 11 days until travel. A care aide will accompany the passenger. Passenger needs assistance (a lift) to board the aircraft. No in-flight medical care required. The conversation ended before financial need was confirmed.
- final: service_region_rationale: Both Wenatchee, WA and Spokane, WA are within Angel Flight West's service region (Washington state is covered).
- final: within_distance_limit_rationale: Wenatchee to Spokane is approximately 170 miles one-way, well within the 900-mile small-plane limit.
- final: minimum_notice_rationale: User indicated approximately 11 days until travel, which exceeds the 5 business day minimum notice requirement for volunteer pilot flights.
- final: requires_small_plane_rationale: The route is short (~170 miles) and within Washington state, making it appropriate for a volunteer pilot small-plane flight.
- final: requires_commercial_rationale: The route is too short and local for a commercial airline pathway.
- final: is_mobile_rationale: User stated the passenger needs a lift into the seat, indicating they cannot board a small aircraft unassisted. This raises a mobility concern for the volunteer small-plane pathway.
- final: is_medically_stable_rationale: User confirmed no in-flight nurse or medical care is needed during the flight, suggesting the passenger is medically stable for air travel.
- final: is_pregnant_rationale: No indication of pregnancy in the conversation.
- final: summary_compelling_or_financial_need_notes: Financial need was not established — the conversation ended before the user responded to the financial hardship question.
- final: summary_sentiment_analysis: The user's responses were very brief and fragmented, suggesting possible difficulty communicating via text or uncertainty about the process. No strong emotional tone was evident, but the brevity may indicate stress or unfamiliarity with the screening process.
- at q1: reason_codes: DATA_INCOMPLETE, MOBILITY_CRITERIA_NOT_MET

### F018 — truth `ineligible` vs pred `manual_review`
- first divergence: q1 (truth `eligible`, pred `ineligible`)
- final: reason_codes: MOBILITY_CRITERIA_NOT_MET
- final: outcome_notes: Passenger is non-weight bearing post-amputation and cannot meet the mobility requirement for volunteer pilot flights. Chatbot offered manual coordinator review or referral to Air Care Alliance. Session ended without a final resolution from the user.
- final: summary_notes: User is seeking a flight from Idaho Falls, ID to Boise, ID for a post-amputation follow-up appointment approximately 9 days out. Route and timeline are within AFW guidelines, but the user is currently non-weight bearing, which disqualifies them from the standard volunteer pilot flight mobility requirement. The chatbot offered a manual coordinator review or referral to Air Care Alliance. The user confirmed the trip is not DV-related. Session ended without a final decision from the user.
- final: service_region_rationale: Both Idaho Falls and Boise are in Idaho, which is within Angel Flight West's service region.
- final: within_distance_limit_rationale: Idaho Falls to Boise is approximately 220 miles, well within the 900-mile small-plane limit.
- final: minimum_notice_rationale: The user indicated travel is approximately 9 days out, which exceeds the 5 business day minimum notice required for volunteer pilot flights.
- final: requires_small_plane_rationale: The route is a short in-state Idaho trip, appropriate for volunteer pilot small-plane travel.
- final: requires_commercial_rationale: The route distance and nature of travel does not indicate a need for commercial airline transport.
- final: is_mobile_rationale: The user stated they are non-weight bearing following an amputation. The chatbot agent identified this as failing the mobility requirement for volunteer pilot flights, as the passenger must be able to step up into the aircraft and bear their own weight independently.
- final: is_medically_stable_rationale: The travel purpose is a post-amputation follow-up appointment, suggesting the passenger is medically stable enough to travel, though no explicit stability confirmation was provided.
- final: is_pregnant_rationale: No indication of pregnancy was mentioned in the conversation.
- final: summary_compelling_or_financial_need_notes: No financial or compelling need was discussed during this conversation.
- final: summary_sentiment_analysis: The user was brief and factual in their responses, providing clarifications when prompted. No strong emotional distress was expressed, though the situation (post-amputation, needing travel assistance) implies vulnerability. The user appeared cooperative but the session ended without a clear resolution.
- at q1: reason_codes: MOBILITY_CRITERIA_NOT_MET

### F020 — truth `ineligible` vs pred `insufficient_information`
- first divergence: q1 (truth `eligible`, pred `ineligible`)
- final: reason_codes: DATA_INCOMPLETE
- final: outcome_notes: The session began as a NICU helicopter transfer request (ineligible), but shifted to a caregiver-only trip at the end. The chatbot had not yet completed screening for the caregiver-only trip — key details such as reason for travel, medical stability, and travel date are still missing. Session ended mid-screening.
- final: summary_notes: The user initially requested help with a NICU helicopter transfer from Reno, NV to Palo Alto, CA. The chatbot correctly identified this as an air ambulance request outside AFW's scope and referred the user to the Air Care Alliance. The user then clarified they wanted to travel alone (without the baby) and mentioned Medicaid as context for financial need. The chatbot was in the process of clarifying the purpose of the caregiver-only trip when the session ended.
- final: service_region_rationale: Both Reno, NV and Palo Alto, CA are within AFW's service region (western US states including NV and CA).
- final: within_distance_limit_rationale: The approximate distance between Reno, NV and Palo Alto, CA is roughly 230 miles, well within the 900-mile small plane limit.
- final: minimum_notice_rationale: The user mentioned 18 days of notice, which exceeds the 5 business day minimum for volunteer small-plane travel.
- final: requires_small_plane_rationale: The route (Reno, NV to Palo Alto, CA) is approximately 230 miles, well within the small-plane range, and the user stated they are mobile.
- final: requires_commercial_rationale: The distance and route do not require commercial travel, and no commercial pathway was indicated.
- final: is_mobile_rationale: The user explicitly stated "I am mobile."
- final: is_medically_stable_rationale: Medical stability of the user/passenger was not confirmed by the chatbot agent during this session.
- final: is_pregnant_rationale: No indication of pregnancy was mentioned in the conversation.
- final: summary_compelling_or_financial_need_notes: User mentioned Medicaid, indicating reliance on public assistance and potential financial hardship.
- final: summary_sentiment_analysis: The user appeared stressed and was providing brief, minimal responses, which may indicate emotional difficulty and urgency related to a NICU situation. Tone was not hostile but was terse and somewhat fragmented throughout.
- at q1: reason_codes: REASON_FOR_TRAVEL_NOT_ELIGIBLE

### F021 — truth `ineligible` vs pred `insufficient_information`
- first divergence: q1 (truth `eligible`, pred `insufficient_information`)
- final: reason_codes: DATA_INCOMPLETE
- final: outcome_notes: Screening was not completed. The chatbot agent was still gathering information about seizure type to assess medical stability when the conversation ended. All other criteria checked so far (location, distance, notice, mobility, financial need) appear favorable.
- final: summary_notes: A caregiver (possibly a mother) is requesting air transportation for a patient traveling from Bakersfield, CA to Los Angeles, CA for epilepsy monitoring, approximately 13 days from now. The passenger experiences seizures most weeks and walks independently. The user mentioned having little savings, indicating financial need. The mother may accompany the patient as a companion. The conversation was incomplete — the chatbot was still awaiting information on seizure type (absence vs. tonic-clonic) to assess medical stability for flight.
- final: service_region_rationale: Both Bakersfield, CA and Los Angeles, CA are within California, which is within AFW's service region.
- final: within_distance_limit_rationale: The one-way distance from Bakersfield to Los Angeles is approximately 110 miles, well within the 900-mile limit for small-plane volunteer travel.
- final: minimum_notice_rationale: User indicated travel is approximately 13 days away, which exceeds the 5 business day minimum notice requirement for volunteer pilot flights.
- final: requires_small_plane_rationale: The route from Bakersfield to Los Angeles is approximately 110 miles, well within the range for volunteer small-plane travel. Commercial pathway is not indicated for this short distance.
- final: requires_commercial_rationale: The distance and route are appropriate for volunteer small-plane travel; commercial pathway is not required.
- final: is_mobile_rationale: User confirmed the passenger "walks alone," indicating sufficient mobility to board and travel on a small aircraft unassisted.
- final: is_medically_stable_rationale: Medical stability could not be fully determined. The passenger has seizures most weeks and is traveling for epilepsy monitoring, but the seizure type (absence vs. tonic-clonic) was not confirmed. The chatbot agent was still gathering this information when the conversation ended.
- final: is_pregnant_rationale: No indication of pregnancy was mentioned in the conversation.
- final: summary_compelling_or_financial_need_notes: User stated they have "little savings," indicating limited financial resources. This supports a finding of financial need for travel assistance.
- final: summary_sentiment_analysis: The user appeared cooperative and willing to provide information, though responses were brief. There was no expressed frustration or urgency. The user seemed calm and focused on obtaining assistance for the patient's medical travel.
- at q1: reason_codes: DATA_INCOMPLETE

### F025 — truth `ineligible` vs pred `manual_review`
- first divergence: q1 (truth `eligible`, pred `insufficient_information`)
- final: reason_codes: EDGE_CASE_COMPLEX
- final: outcome_notes: Passenger is traveling for radiation treatment in LA from Fresno with three companions. All core eligibility criteria appear met (mobile, stable, financial need, within service region and distance), but the number of companions (3) exceeds the typical capacity for volunteer flights. Case sent for manual coordinator review.
- final: summary_notes: User is requesting travel for a patient undergoing radiation treatment in Los Angeles from Fresno, CA. Travel is needed in approximately 14 days. The passenger walks independently, is medically stable, and the user reports financial hardship. The key complication is that three companions are requested, which exceeds standard volunteer flight capacity and triggered a manual review flag.
- final: service_region_rationale: Both Fresno, CA and Los Angeles, CA are within California, which is well within AFW's service region.
- final: within_distance_limit_rationale: The route from Fresno to Los Angeles is approximately 220 miles, which is well within the 900-mile small-plane distance limit.
- final: minimum_notice_rationale: The user mentioned travel is in approximately 14 days, which exceeds the 5 business day minimum notice requirement for volunteer pilot flights.
- final: requires_small_plane_rationale: The route is short (~220 miles), within California, and within AFW's small-plane volunteer pilot network coverage area.
- final: requires_commercial_rationale: The distance and route are appropriate for a volunteer small-plane flight; commercial pathway is not indicated.
- final: is_mobile_rationale: The user confirmed the passenger "walks fine" and can move without assistance.
- final: is_medically_stable_rationale: The user confirmed the passenger is "stable" and does not require medical equipment or monitoring during the flight.
- final: is_pregnant_rationale: No indication of pregnancy was mentioned in the conversation.
- final: summary_compelling_or_financial_need_notes: User stated they cannot pay for travel, indicating clear financial hardship. The medical necessity of radiation treatment adds a compelling need dimension as well.
- final: summary_sentiment_analysis: The user was cooperative and concise throughout the conversation, providing direct answers. Their responses suggest urgency and financial stress, but no frustration or distress was evident.
- at q1: reason_codes: DATA_INCOMPLETE

### F026 — truth `ineligible` vs pred `eligible`
- first divergence: q1 (truth `eligible`, pred `insufficient_information`)
- final: reason_codes: OTHER
- final: outcome_notes: Caregiver traveling to support father undergoing chemotherapy in San Francisco from Modesto. User is mobile, medically stable, on disability income (financial need confirmed), and travel is 11 days out. Chatbot determined eligible for volunteer pilot program. Coordinator will verify with medical provider.
- final: summary_notes: User is a caregiver (not the patient) traveling from Modesto, CA to San Francisco, CA to support their father who is undergoing chemotherapy. User confirmed they are mobile, medically stable, not pregnant, and on disability income. Travel is approximately 11 days away. No DV context. Chatbot determined the trip appears eligible for the volunteer pilot program and directed user to complete an online application.
- final: service_region_rationale: Both Modesto, CA and San Francisco, CA are within California, which is within AFW's service region.
- final: within_distance_limit_rationale: The distance from Modesto to San Francisco is approximately 90 miles, well within the 900-mile limit for volunteer small-plane travel.
- final: minimum_notice_rationale: User indicated travel is approximately 11 days away, which meets the minimum 5 business days notice required for volunteer pilot flights.
- final: requires_small_plane_rationale: The route is short (~90 miles) and within CA, making it well suited for a volunteer small-plane flight. The chatbot confirmed the volunteer pilot program pathway.
- final: requires_commercial_rationale: Distance and route do not require commercial travel; the volunteer pilot pathway was recommended.
- final: is_mobile_rationale: User confirmed they are mobile and able to travel on a small aircraft.
- final: is_medically_stable_rationale: User confirmed they are medically stable for travel with no need for oxygen, monitoring, or medical equipment during the flight.
- final: is_pregnant_rationale: No indication of pregnancy was raised in the conversation.
- final: summary_compelling_or_financial_need_notes: User is on disability income, indicating significant financial hardship in covering travel costs independently. Travel is to support a parent undergoing cancer treatment, adding a compelling humanitarian dimension.
- final: summary_sentiment_analysis: User was brief and direct throughout the conversation, providing concise responses. They appeared focused and purposeful, with no signs of distress or frustration. Their responses suggest quiet determination to support their father through a serious illness.
- at q1: reason_codes: DATA_INCOMPLETE

### F027 — truth `ineligible` vs pred `eligible`
- first divergence: q1 (truth `eligible`, pred `insufficient_information`)
- final: reason_codes: OTHER
- final: outcome_notes: Patient traveling solo from San Jose to Sacramento for a cardiology follow-up. Meets mobility, medical stability, notice, and service region criteria. Chatbot presented volunteer pilot pathway and provided application link. User later mentioned ability to pay for Southwest — coordinator should follow up on financial need and appropriate pathway.
- final: summary_notes: User requested a flight from San Jose, CA to Sacramento, CA for a cardiology follow-up appointment approximately 9 days away. The patient is traveling solo, is mobile, and is medically stable. The chatbot determined the volunteer pilot pathway was appropriate and provided an application link. Toward the end of the conversation, the user mentioned they could afford a Southwest flight, which was noted for coordinator follow-up.
- final: service_region_rationale: Both San Jose, CA and Sacramento, CA are within California, which is part of AFW's service region.
- final: within_distance_limit_rationale: The approximate distance from San Jose to Sacramento is roughly 90 miles, well within the 900-mile small plane limit.
- final: minimum_notice_rationale: The user indicated travel is approximately 9 days away, which exceeds the 5 business day minimum notice requirement for volunteer pilot flights.
- final: requires_small_plane_rationale: The route is short (~90 miles), within California, and the chatbot directed the user toward the volunteer pilot program, noting small aircraft and volunteer pilots. The user also mentioned they can afford Southwest, but the chatbot had already presented the volunteer pilot pathway.
- final: requires_commercial_rationale: The chatbot did not route the user to commercial/Alaska Airlines. The user mentioned they could pay for Southwest, but this was raised after the volunteer pathway was already presented, and no commercial pathway determination was made by the chatbot agent.
- final: is_mobile_rationale: The user responded "Fine" when asked whether the patient can step up into the aircraft, move in and out of the seat, and sit upright with a seatbelt without assistance — indicating mobility criteria are met.
- final: is_medically_stable_rationale: The user responded "Stable" when asked about medical monitoring or equipment needs during the flight, indicating the patient is medically stable for non-emergency air travel.
- final: is_pregnant_rationale: No indication of pregnancy was mentioned in the conversation.
- final: summary_compelling_or_financial_need_notes: User stated they can pay for Southwest Airlines, suggesting financial need may not be present. The chatbot deferred this question to the coordinator rather than reassessing eligibility.
- final: summary_sentiment_analysis: The user was brief and somewhat terse throughout the conversation, providing minimal responses (e.g., "Fine," "Stable," "Solo"). The mention of being able to afford Southwest may suggest some uncertainty about whether the program is appropriate for them, but overall the user engaged cooperatively and completed the session.
- at q1: reason_codes: DATA_INCOMPLETE

### F028 — truth `ineligible` vs pred `insufficient_information`
- first divergence: q1 (truth `eligible`, pred `insufficient_information`)
- final: reason_codes: DATA_INCOMPLETE, FINANCIAL_CRITERIA_NOT_MET
- final: outcome_notes: Screening is incomplete. The passenger may not meet the financial or compelling need criteria as insurance reportedly covers transportation. The chatbot agent asked a clarifying follow-up question but the user did not provide a conclusive answer before the session ended.
- final: summary_notes: Patient is seeking a flight from Oakland, CA to Portland, OR for an orthopedic consultation. Travel is approximately 13 days away. Passenger is traveling alone, is mobile, and does not require in-flight medical monitoring. User confirmed the case is not DV-related. When asked about financial need, the user stated insurance covers transportation. Chatbot asked a follow-up clarifying question about whether there is still a hardship, but the session ended before a clear answer was given.
- final: service_region_rationale: Both Oakland, CA and Portland, OR are within AFW's service region (Western US states including CA and OR).
- final: within_distance_limit_rationale: Oakland to Portland is approximately 550 miles, which is within the 900-mile limit for small-plane volunteer flights.
- final: minimum_notice_rationale: User indicated approximately 13 days of notice, which exceeds the 5 business day minimum for volunteer pilot flights.
- final: requires_small_plane_rationale: The route (Oakland to Portland, ~550 miles) is within small-plane range, and no specific indicators suggest a commercial pathway is needed.
- final: requires_commercial_rationale: No indicators in the conversation suggest a commercial airline pathway is needed. The route is within small-plane range and the passenger reported no mobility or medical equipment issues.
- final: is_mobile_rationale: The user confirmed mobility when asked about the passenger's ability to board and sit in a small aircraft, responding "Ok mobility."
- final: is_medically_stable_rationale: User stated no in-flight medical monitoring, nursing care, or medical equipment (e.g., oxygen) would be required, suggesting the passenger is medically stable for non-emergency air travel.
- final: is_pregnant_rationale: No indication of pregnancy was mentioned in the conversation.
- final: summary_compelling_or_financial_need_notes: User stated insurance covers transportation to Portland, which may indicate no financial hardship. It is unclear whether there is a compelling transportation need beyond cost. The screening was incomplete on this criterion.
- final: summary_sentiment_analysis: The user was brief and cooperative, providing short but relevant answers. Responses were matter-of-fact with no emotional distress detected. The user did not elaborate beyond direct answers, suggesting a transactional and efficient approach to the conversation.
- at q1: reason_codes: DATA_INCOMPLETE

### F036 — truth `eligible` vs pred `ineligible`
- first divergence: q1 (truth `eligible`, pred `insufficient_information`)
- final: reason_codes: INSUFFICIENT_NOTICE
- final: outcome_notes: Patient is otherwise a strong candidate (medical need, financial need via SSDI, mobile, medically stable, within service region), but the appointment is only 3 days away, which does not meet the 5 business day minimum notice requirement for volunteer pilot flights.
- final: summary_notes: Patient is traveling from Redding, CA to Sacramento, CA for a burn clinic follow-up appointment. They are on SSDI, mobile, traveling solo, and do not require medical monitoring. The only barrier is insufficient notice — the appointment is 3 days away, and volunteer flights require at least 5 business days of lead time. The chatbot referred the user to Air Care Alliance for shorter-notice options.
- final: service_region_rationale: Both Redding, CA and Sacramento, CA are within California, which is within AFW's service region.
- final: within_distance_limit_rationale: Redding to Sacramento is approximately 162 miles, well within the 900-mile small-plane limit.
- final: minimum_notice_rationale: User stated the appointment is in 3 days. Volunteer pilot flights require at least 5 business days of notice. This trip does not meet the minimum notice requirement.
- final: requires_small_plane_rationale: The route from Redding to Sacramento is short (~162 miles) and appropriate for a volunteer small-plane flight. The user confirmed they can walk and get around on their own, travel solo, and do not need medical monitoring on the flight.
- final: requires_commercial_rationale: No indicators suggest commercial travel is necessary. Distance is short and passenger is mobile and medically stable.
- final: is_mobile_rationale: User explicitly stated "I can walk and get around on my own" and confirmed they will be traveling solo.
- final: is_medically_stable_rationale: User stated they do not need medical monitoring on the flight, and they are mobile and independent, suggesting they are medically stable for non-emergency air travel.
- final: is_pregnant_rationale: No indication of pregnancy in the conversation.
- final: summary_compelling_or_financial_need_notes: User is on SSDI, indicating financial hardship and demonstrating a compelling need for assistance with transportation costs to a medical follow-up appointment.
- final: summary_sentiment_analysis: The user was persistent and cooperative, continuing to provide additional information (mobility, medical stability, travel solo) even after being told the timing was the issue. Sentiment appears hopeful and determined, though the user may have been frustrated by the focus on timing rather than their qualifications.
- at q1: reason_codes: DATA_INCOMPLETE

### F037 — truth `eligible` vs pred `ineligible`
- first divergence: q1 (truth `eligible`, pred `insufficient_information`)
- final: reason_codes: INSUFFICIENT_NOTICE
- final: outcome_notes: Patient is traveling from Stockton, CA to San Francisco, CA for a medical (MFM) appointment. They are mobile, medically stable, and have a financial need (single income). However, the trip is only 2 days away, which does not meet the 5 business day minimum notice requirement for volunteer pilot flights. Case was deemed ineligible due to insufficient notice.
- final: summary_notes: User is a patient traveling from Stockton, CA to San Francisco, CA for an MFM (Maternal-Fetal Medicine) appointment in 2 days. They are self-ambulatory, do not need in-flight medical monitoring, and are on a single income. The spouse may accompany them. The case was ruled ineligible solely due to insufficient advance notice (2 days vs. required 5 business days). The chatbot referred the user to Air Care Alliance for short-notice options.
- final: service_region_rationale: Both Stockton, CA and San Francisco, CA are within AFW's service region (California is a covered state).
- final: within_distance_limit_rationale: The approximate one-way distance from Stockton, CA to San Francisco, CA is roughly 85 miles, well within the 900-mile small-plane limit.
- final: minimum_notice_rationale: The user stated the appointment is in 2 days. The volunteer pilot pathway requires at least 5 business days of advance notice, which is not met in this case.
- final: requires_small_plane_rationale: The route from Stockton, CA to San Francisco, CA (~85 miles) is well-suited for a volunteer small-plane flight and does not require commercial air travel.
- final: requires_commercial_rationale: The distance (~85 miles) and route do not necessitate commercial air travel; this was not identified as a commercial pathway case.
- final: is_mobile_rationale: The user stated "I can walk and get around on my own," indicating they are independently mobile.
- final: is_medically_stable_rationale: The user stated they do not need medical monitoring on the flight, suggesting medical stability for non-emergency air travel.
- final: is_pregnant_rationale: The user did not confirm or deny pregnancy. The chatbot asked but did not receive a clear answer about pregnancy status.
- final: summary_compelling_or_financial_need_notes: User is on a single income, indicating financial hardship. The chatbot acknowledged this as a qualifying need, but the case could not proceed due to insufficient notice.
- final: summary_sentiment_analysis: The user was persistent and cooperative, repeatedly providing additional information (mobility, no need for in-flight monitoring, financial situation, possible companion) in hopes of qualifying. They appeared motivated and somewhat frustrated but remained calm throughout.
- at q1: reason_codes: DATA_INCOMPLETE

### F039 — truth `eligible` vs pred `ineligible`
- first divergence: q1 (truth `eligible`, pred `ineligible`)
- final: reason_codes: DISTANCE_TOO_GREAT
- final: outcome_notes: The route from Tacoma, WA to Seattle, WA is too short (~35 miles) for Angel Flight West air travel to be practical. The chatbot agent determined the trip ineligible solely on distance grounds. User was referred to American Cancer Society Road to Recovery, Air Care Alliance, 211, and hospital social work resources.
- final: summary_notes: User is a solo caregiver for their husband who is undergoing chemotherapy in Seattle, WA. They are traveling from Tacoma, WA. They noted financial hardship, the ability to walk/self-transfer, no need for medical monitoring, and that the appointment is in 10 days. Despite meeting several eligibility factors, the trip was deemed ineligible due to the short distance between Tacoma and Seattle.
- final: service_region_rationale: Both Tacoma, WA and Seattle, WA are within AFW's service region (Pacific Northwest). However, the route was deemed ineligible due to insufficient distance, not service region.
- final: within_distance_limit_rationale: The distance from Tacoma to Seattle is approximately 35 miles, which is far too short for air travel to be practical. The chatbot agent explicitly stated the distance is too short for Angel Flight West to assist with.
- final: minimum_notice_rationale: User mentioned the appointment is in 10 days, which meets minimum notice requirements. However, the trip was deemed ineligible due to distance, not notice.
- final: requires_small_plane_rationale: The route from Tacoma to Seattle is too short for a small plane to be practical. The chatbot agent determined the trip is ineligible on distance grounds.
- final: requires_commercial_rationale: The distance is far too short for commercial air travel to be appropriate or practical for this route.
- final: is_mobile_rationale: The user stated they can walk and get around on their own.
- final: is_medically_stable_rationale: The user stated they do not need medical monitoring on the flight, suggesting medical stability.
- final: is_pregnant_rationale: No indication of pregnancy in the conversation.
- final: summary_compelling_or_financial_need_notes: User explicitly stated they are on hardship and are a solo caregiver for a husband undergoing chemotherapy, indicating both financial and compelling transportation need.
- final: summary_sentiment_analysis: The user appeared persistent and determined, repeatedly providing additional information (mobility, medical stability, notice, hardship) in hopes of qualifying. The tone was urgent and somewhat frustrated, understandable given the stressful caregiving situation and financial hardship.
- at q1: reason_codes: DISTANCE_TOO_GREAT

