# Failure Analysis

## Run Summary
- personas: 120
- scored final outcomes: 120
- final outcome accuracy: 56.7%
- incorrect matches: 52
- unscored final outcomes: 0

## Error Concentration By Truth Class
- manual_review: 20 mismatches
- insufficient_information: 16 mismatches
- eligible: 9 mismatches
- ineligible: 7 mismatches

## Confusion Pairs
- truth `insufficient_information` predicted `manual_review`: 15
- truth `manual_review` predicted `insufficient_information`: 10
- truth `eligible` predicted `manual_review`: 5
- truth `manual_review` predicted `eligible`: 5
- truth `manual_review` predicted `ineligible`: 5
- truth `ineligible` predicted `manual_review`: 4
- truth `eligible` predicted `ineligible`: 3
- truth `ineligible` predicted `insufficient_information`: 2
- truth `ineligible` predicted `eligible`: 1
- truth `eligible` predicted `insufficient_information`: 1

## First Divergence Checkpoint
- q8: 47 mismatches
- q7: 45 mismatches
- q2: 37 mismatches
- q3: 37 mismatches
- q1: 36 mismatches
- q4: 36 mismatches
- q5: 34 mismatches
- q6: 34 mismatches

## Session Rationale — Outcome Reason Codes (failures only)
- `DATA_INCOMPLETE`: 31
- `EDGE_CASE_COMPLEX,DATA_INCOMPLETE`: 3
- `DISTANCE_TOO_GREAT,REASON_FOR_TRAVEL_NOT_ELIGIBLE`: 3
- `INSUFFICIENT_NOTICE`: 2
- `EDGE_CASE_COMPLEX`: 2
- `DATA_INCOMPLETE,INSUFFICIENT_NOTICE`: 1
- `DISTANCE_TOO_GREAT`: 1
- `DATA_INCOMPLETE,EDGE_CASE_COMPLEX`: 1
- `REASON_FOR_TRAVEL_NOT_ELIGIBLE`: 1
- `REASON_FOR_TRAVEL_NOT_ELIGIBLE,MOBILITY_CRITERIA_NOT_MET`: 1

## Session Rationale — Final outcome_notes (failures only)
- (1x) Unable to determine advance notice (travel date), which is required to complete screening. Mobility status may also need clarification.
- (1x) Coordinator review required due to missing exact travel date and potential for insufficient notice.
- (1x) Unclear if passenger is eligible; requires coordinator review due to medical complexity (NICU/possible need for medical transport and lack of mobility).
- (1x) Manual review required due to possible medical instability (recurrent seizures and unclear inflight needs).
- (1x) Screening incomplete: departure date not yet provided, minimum notice cannot be confirmed.
- (1x) Case needs coordinator follow-up to confirm number of total travelers/companions before eligibility determination.
- (1x) Caregiver requesting transport to support father receiving chemo; meets mobility, medical, financial, regional, and timing criteria.
- (1x) Request is ineligible due to insufficient minimum notice—user's appointment is in 3 days, volunteer flights require at least 5 business days' notice.

## Session Rationale — Criterion fields cited on failures
- (7x) dv_context_rationale: User explicitly stated 'Not a domestic violence case.'
- (4x) dv_in_shelter_rationale: Not a DV case.
- (4x) dv_provider_rationale: Not a DV case.
- (3x) dv_context_rationale: No mention of domestic violence context.
- (3x) dv_context_rationale: User stated 'Not a domestic violence case.'
- (3x) dv_in_shelter_rationale: Not a domestic violence case.
- (3x) dv_provider_rationale: Not a domestic violence case.
- (2x) is_pregnant_rationale: No pregnancy mentioned.
- (2x) dv_context_rationale: User explicitly stated 'Not dv'.
- (2x) is_medically_stable_rationale: User stated 'I dont need medical monitoring on the flight.'
- (2x) is_pregnant_rationale: No information provided.
- (2x) is_pregnant_rationale: No information provided about pregnancy status.

## Rationale Evidence By Confusion Pattern
### truth `insufficient_information` → predicted `manual_review`
- F061: reason_codes: DATA_INCOMPLETE | outcome_notes: Insufficient information: trip purpose, route, and eligibility criteria not provided. Chatbot referred for coordinator follow-up. | summary_notes: User inquired about a flight but declined to provide trip reason, route, or details; chatbot explained that a coordinator would reach out for follow-up.
- F062: reason_codes: DATA_INCOMPLETE | outcome_notes: Details needed for travel purpose and destination are missing. Coordinator follow-up required. | summary_notes: User is in Portland, Oregon, needs a flight next month, but declined to provide the reason for travel or destination. Coordinator follow-up is required.
- F065: reason_codes: DATA_INCOMPLETE | outcome_notes: Coordinator review required due to missing key information (origin, reason for travel, date). | summary_notes: User seeks help for travel to Mayo Clinic but did not provide city/state of origin or exact appointment date. Agent requested contact info for coordinator follow-up.
- F065 @ q5: reason_codes: DATA_INCOMPLETE
### truth `manual_review` → predicted `insufficient_information`
- F093: reason_codes: DATA_INCOMPLETE | outcome_notes: Screening not fully complete; user not yet confirmed able to board small plane unassisted and complete application. | summary_notes: User seeks transport from Tucson, AZ to Phoenix, AZ for medical treatment in 12 days; usually able to board small planes unaided but may need a hand on stairs, no nurse required, and faces Medicaid financial gaps; not a DV situation.
- F093 @ q1: reason_codes: DATA_INCOMPLETE
- F096: reason_codes: DATA_INCOMPLETE | outcome_notes: Screening is in progress—awaiting user's response about recent seizure activity and in-flight medical needs. | summary_notes: User requested help traveling from Carson City, NV to Sacramento, CA for cardiology. User can walk/transfer without help, has had a single seizure last year, may have mother join, and is on a fixed income. No DV context. Awaiting answer regarding recent seizure activity or need for medical monitoring.
- F096 @ q1: reason_codes: DATA_INCOMPLETE
### truth `eligible` → predicted `manual_review`
- F038: reason_codes: EDGE_CASE_COMPLEX | outcome_notes: Domestic violence relocation scenario with advocate assigned; routed for manual review for further processing. | summary_notes: User requests DV shelter relocation flight from San Diego to Phoenix. Has shelter advocate, no funds, can walk, no medical monitoring needed, appointment in 11 days. Passenger number still pending.
- F038 @ q1: reason_codes: DATA_INCOMPLETE
- F041: reason_codes: EDGE_CASE_COMPLEX,DATA_INCOMPLETE | outcome_notes: Case sent to coordinator for review because it is unclear if the pediatric patient can sit upright with seat-belt. | summary_notes: Caregiver requested flight for pediatric oncology for son, Modesto CA to Oakland CA, indicated financial need, confirmed not a DV case, meets minimum notice and mobility criteria for self, but it's unclear if son can sit with seat-belt—needs coordinator review.
- F041 @ q1: reason_codes: DATA_INCOMPLETE
### truth `manual_review` → predicted `eligible`
- F101: outcome_notes: All criteria met for commercial airline ticket for medical treatment; financial need, medical stability, and mobility confirmed. | summary_notes: User needs to fly from Honolulu, HI to San Francisco, CA for oncology. Is mobile, does not need medical monitoring, and reported hardship due to 'island costs'. Spouse will accompany. | service_region_rationale: Honolulu, HI and San Francisco, CA are both within Angel Flight West's service region; this was confirmed by the user.
- F101 @ q1: reason_codes: DATA_INCOMPLETE
- F112: outcome_notes: User is eligible for a volunteer pilot flight due to mobility, stability, compelling rural access need, route within AFW region and distance limits, and adequate notice. | summary_notes: User requested transport from Butte, MT to Salt Lake City, UT for endocrine treatment in about 11 days; ambulatory and financially/transportationally challenged due to rural location. Agent approved for small-plane flight and directed to application form. | service_region_rationale: Both Butte, MT and Salt Lake City, UT are within the AFW service region as stated by the user.
- F112 @ q1: reason_codes: DATA_INCOMPLETE
### truth `manual_review` → predicted `ineligible`
- F103: reason_codes: REASON_FOR_TRAVEL_NOT_ELIGIBLE,MOBILITY_CRITERIA_NOT_MET | outcome_notes: Trip reason is not medical, and the user reports mobility limitations incompatible with small-plane travel. | summary_notes: User needs to travel from Corvallis, OR to San Francisco, CA for a 'trial' in approximately 12 days, traveling alone, cites fatigue affecting stair use, is medically stable and has financial need due to trial costs. Clarified that this is not a domestic violence case.
- F103 @ q1: reason_codes: DATA_INCOMPLETE
- F104: reason_codes: DISTANCE_TOO_GREAT,REASON_FOR_TRAVEL_NOT_ELIGIBLE | outcome_notes: Trip is not eligible due to very short distance between Mesa and Phoenix. | summary_notes: User requested flight from Mesa, AZ to Phoenix, AZ for surgery. User confirmed ability to walk and medical stability, stated hardship, but route is too short for Angel Flight West eligibility.
- F104 @ q1: reason_codes: DISTANCE_TOO_GREAT
### truth `ineligible` → predicted `manual_review`
- F015: reason_codes: DATA_INCOMPLETE,INSUFFICIENT_NOTICE | outcome_notes: Coordinator review required due to missing exact travel date and potential for insufficient notice. | summary_notes: User inquired about travel from Honolulu, HI to San Francisco, CA for a medical specialist, needs to travel with one companion, confirmed financial hardship, and is mobile and medically stable. Did not provide exact travel date.
- F015 @ q1: reason_codes: DATA_INCOMPLETE
- F020: reason_codes: EDGE_CASE_COMPLEX,DATA_INCOMPLETE | outcome_notes: Unclear if passenger is eligible; requires coordinator review due to medical complexity (NICU/possible need for medical transport and lack of mobility). | summary_notes: User requested help transporting a NICU patient (likely a newborn) by helicopter from Reno, NV to Palo Alto, CA in about 18 days. Medical stability and need for aerosol medical transport unclear.
- F021: reason_codes: EDGE_CASE_COMPLEX,DATA_INCOMPLETE | outcome_notes: Manual review required due to possible medical instability (recurrent seizures and unclear inflight needs). | summary_notes: Patient requesting help for travel from Bakersfield to Los Angeles for epilepsy monitoring in about 13 days. User can walk alone, has seizures most weeks, mother may travel as companion, requires clarification on in-flight medical needs.

## Incorrect Personas (with session rationale)
### F011 — truth `ineligible` vs pred `insufficient_information`
- first divergence: q1 (truth `eligible`, pred `insufficient_information`)
- final: reason_codes: DATA_INCOMPLETE
- final: outcome_notes: Unable to determine advance notice (travel date), which is required to complete screening. Mobility status may also need clarification.
- final: summary_notes: User requested help traveling alone from Bellingham, WA to Olympia, WA for chemotherapy, shared SSDI status, stated slow stair mobility, and does not require in-flight medical care. Did not provide definite travel date.
- final: service_region_rationale: User's origin (Bellingham, WA) and destination (Olympia, WA) are both in Washington, which is within AFW's service region.
- final: within_distance_limit_rationale: Bellingham to Olympia is approximately 160 miles, well within the 900-mile limit for small-plane flights.
- final: minimum_notice_rationale: User only stated needing to travel 'in 4 days,' and it is unclear if this is at least 5 business days. The chatbot repeated the question several times without receiving a definitive answer.
- final: requires_small_plane_rationale: Route is within the distance and service region, and the chatbot is screening for a volunteer-pilot pathway.
- final: requires_commercial_rationale: There is no indication that commercial is required; volunteer-pilot pathway is considered.
- final: is_mobile_rationale: User said they are 'slow on stairs,' which may indicate limited mobility; however, the agent did not explicitly confirm eligibility for small-plane criteria.
- final: is_medically_stable_rationale: User reported no need for in-flight medical care and did not report medical instability.
- final: is_pregnant_rationale: No pregnancy mentioned.
- final: summary_compelling_or_financial_need_notes: User stated SSDI as sole income, indicating financial need.
- final: summary_sentiment_analysis: User's tone is brief and factual, with no explicit distress.
- at q1: reason_codes: DATA_INCOMPLETE

### F015 — truth `ineligible` vs pred `manual_review`
- first divergence: q1 (truth `eligible`, pred `insufficient_information`)
- final: reason_codes: DATA_INCOMPLETE,INSUFFICIENT_NOTICE
- final: outcome_notes: Coordinator review required due to missing exact travel date and potential for insufficient notice.
- final: summary_notes: User inquired about travel from Honolulu, HI to San Francisco, CA for a medical specialist, needs to travel with one companion, confirmed financial hardship, and is mobile and medically stable. Did not provide exact travel date.
- final: service_region_rationale: The agent identified both Honolulu (HI) and San Francisco (CA) as valid city/state pairs; Hawaii and California are within AFW’s service region.
- final: within_distance_limit_rationale: Honolulu to San Francisco is approximately 2400 miles and over open ocean, not within small-plane limits.
- final: minimum_notice_rationale: The agent could not determine if minimum notice is met because a specific date was not provided; requesting on a Monday for that Monday likely does not meet minimum notice for commercial pathway.
- final: requires_small_plane_rationale: Distance and route from Honolulu to San Francisco cannot be served by small planes.
- final: requires_commercial_rationale: The agent treated this as a potential Alaska Airlines commercial flight route (HI to mainland CA).
- final: is_mobile_rationale: User stated they are 'ok on planes' and do not require in-flight monitoring.
- final: is_medically_stable_rationale: User confirmed they do not require in-flight medical care or monitoring.
- final: is_pregnant_rationale: No information provided suggesting passenger is pregnant.
- final: summary_compelling_or_financial_need_notes: User stated they have no funding for travel, indicating financial hardship.
- final: summary_sentiment_analysis: User was cooperative and responsive, provided needed details when prompted.
- at q1: reason_codes: DATA_INCOMPLETE

### F020 — truth `ineligible` vs pred `manual_review`
- first divergence: q1 (truth `eligible`, pred `manual_review`)
- final: reason_codes: EDGE_CASE_COMPLEX,DATA_INCOMPLETE
- final: outcome_notes: Unclear if passenger is eligible; requires coordinator review due to medical complexity (NICU/possible need for medical transport and lack of mobility).
- final: summary_notes: User requested help transporting a NICU patient (likely a newborn) by helicopter from Reno, NV to Palo Alto, CA in about 18 days. Medical stability and need for aerosol medical transport unclear.
- final: service_region_rationale: User stated origin is Reno, NV and destination is Palo Alto, CA. Both are within AFW service region.
- final: within_distance_limit_rationale: Distance between Reno, NV and Palo Alto, CA is well under 900 miles.
- final: minimum_notice_rationale: User requested help approximately 18 days in advance, which meets minimum notice.
- final: requires_small_plane_rationale: User's locations and advance notice fit typical volunteer pilot pathway, pending medical review.
- final: requires_commercial_rationale: No indication commercial flight required at this stage.
- final: is_mobile_rationale: User referenced NICU and helicopter, strongly suggesting the passenger (likely a newborn) is not mobile.
- final: is_medically_stable_rationale: User mentioned NICU and helicopter, triggering agent's follow-up about medical monitoring needs.
- final: is_pregnant_rationale: No information provided suggesting pregnancy.
- final: summary_compelling_or_financial_need_notes: User is seeking help with NICU-related medical transport, which typically indicates compelling need.
- final: summary_sentiment_analysis: User's tone is urgent and factual.

### F021 — truth `ineligible` vs pred `manual_review`
- first divergence: q1 (truth `eligible`, pred `insufficient_information`)
- final: reason_codes: EDGE_CASE_COMPLEX,DATA_INCOMPLETE
- final: outcome_notes: Manual review required due to possible medical instability (recurrent seizures and unclear inflight needs).
- final: summary_notes: Patient requesting help for travel from Bakersfield to Los Angeles for epilepsy monitoring in about 13 days. User can walk alone, has seizures most weeks, mother may travel as companion, requires clarification on in-flight medical needs.
- final: service_region_rationale: User specified travel from Bakersfield, CA to Los Angeles, CA, both of which are within AFW's service region.
- final: within_distance_limit_rationale: Distance is approximately 110 miles, well within the typical limits for small-plane volunteer flights.
- final: minimum_notice_rationale: User stated they would travel in 13 days, which is more than the required 5 business days for volunteer pilot pathway.
- final: requires_small_plane_rationale: Short distance, in-state, within region, no indicated need for commercial flight.
- final: requires_commercial_rationale: No indication that a commercial flight is required; route appropriate for small-plane volunteer flight.
- final: is_mobile_rationale: User confirmed that they can walk alone.
- final: is_medically_stable_rationale: User indicated seizures occur most weeks; additional clarification needed regarding risk during flight and potential need for in-flight medical care.
- final: is_pregnant_rationale: No mention of pregnancy in the conversation.
- final: summary_compelling_or_financial_need_notes: Compelling need for assistance with medical transportation to Los Angeles for a multi-day hospital stay.
- final: summary_sentiment_analysis: User is cooperative, clear, and seeking support for a medical need; no distress observed.
- at q1: reason_codes: DATA_INCOMPLETE

### F024 — truth `ineligible` vs pred `insufficient_information`
- first divergence: q1 (truth `eligible`, pred `insufficient_information`)
- final: reason_codes: DATA_INCOMPLETE
- final: outcome_notes: Screening incomplete: departure date not yet provided, minimum notice cannot be confirmed.
- final: summary_notes: User seeking help for four tickets from Anchorage, AK to Seattle, WA for ongoing cancer treatment (chemo), requesting airline travel for patient, spouse, and two children. User confirms stability for commercial flight and implies financial need due to high Alaska airline costs. Has not yet provided specific travel date.
- final: service_region_rationale: User stated travel is from Anchorage, AK to Seattle, WA. Both are within AFW's service region (AK, WA).
- final: within_distance_limit_rationale: The approximate distance is 1440 miles (Anchorage to Seattle), exceeding 900 miles; pathway is likely commercial airline (Alaska Airlines partner).
- final: minimum_notice_rationale: The user has not yet provided a travel date; minimum notice cannot be determined yet.
- final: requires_small_plane_rationale: Route and distance suggest commercial airline, not small plane.
- final: requires_commercial_rationale: The user is traveling between Anchorage and Seattle, a typical commercial route in AFW's region, and is medically stable and able to sit on a standard airline seat.
- final: is_mobile_rationale: User indicated airline is acceptable and made no mention of mobility limitations, so assumed able to sit upright and board independently.
- final: is_medically_stable_rationale: User stated 'stable' in response to medical status and no need for medical staff on flight.
- final: is_pregnant_rationale: No indication from the user of pregnancy.
- final: summary_compelling_or_financial_need_notes: User directly mentioned concerns regarding Alaska airline costs, suggesting financial hardship or compelling cost barrier for out-of-state medical travel.
- final: summary_sentiment_analysis: User appears cooperative, brief, and oriented toward receiving help. Some stress suggested by repeated cost and urgency notes.
- at q1: reason_codes: DATA_INCOMPLETE

### F025 — truth `ineligible` vs pred `manual_review`
- first divergence: q1 (truth `eligible`, pred `insufficient_information`)
- final: reason_codes: DATA_INCOMPLETE
- final: outcome_notes: Case needs coordinator follow-up to confirm number of total travelers/companions before eligibility determination.
- final: summary_notes: Patient seeking assistance from Fresno to Los Angeles for medical radiation appointment. Provided info on mobility, financial need, and schedule. Needs three seats but exact count unclear. Coordinator follow-up pending.
- final: service_region_rationale: Both Fresno and Los Angeles are in California, within AFW's service region, as indicated by the user's input.
- final: within_distance_limit_rationale: The one-way distance from Fresno to Los Angeles (~220 miles) is within the typical 900-mile limit for small planes.
- final: minimum_notice_rationale: Travel is requested 14 days from now, which meets the minimum 5 business day notice required for a volunteer pilot flight.
- final: requires_small_plane_rationale: The agent stated the route could fit the volunteer-pilot program and flight distance fits volunteer pathway.
- final: requires_commercial_rationale: Commercial air was not discussed, pathway remains volunteer small-plane.
- final: is_mobile_rationale: The user confirmed 'walks fine' for mobility and did not state any mobility limitation.
- final: is_medically_stable_rationale: The user confirmed medical stability by stating 'stable.'
- final: is_pregnant_rationale: No pregnancy reported or discussed.
- final: summary_compelling_or_financial_need_notes: User stated 'can't pay,' indicating financial hardship.
- final: summary_sentiment_analysis: User was cooperative, informative, and concise in responses, displaying a neutral and straightforward tone.
- at q1: reason_codes: DATA_INCOMPLETE

### F026 — truth `ineligible` vs pred `eligible`
- first divergence: q1 (truth `eligible`, pred `insufficient_information`)
- final: outcome_notes: Caregiver requesting transport to support father receiving chemo; meets mobility, medical, financial, regional, and timing criteria.
- final: summary_notes: Caregiver requested volunteer flight from Modesto to San Francisco, CA for father's chemotherapy; user is stable, mobile, not DV, and has financial need.
- final: service_region_rationale: Both Modesto and San Francisco are in California, within the AFW western US service region.
- final: within_distance_limit_rationale: Modesto to San Francisco is approximately 90 miles, within the typical small-plane service limit.
- final: minimum_notice_rationale: User requested travel in 11 days, which meets the minimum 5 business day notice for volunteer-pilot flights.
- final: requires_small_plane_rationale: Travel is suitable for a volunteer small plane flight due to short distance and service region.
- final: requires_commercial_rationale: Volunteer pilot (small plane) pathway applies; commercial not indicated for this route.
- final: is_mobile_rationale: User confirmed they are mobile.
- final: is_medically_stable_rationale: User reported they are stable.
- final: is_pregnant_rationale: No pregnancy mentioned or suggested in the conversation.
- final: summary_compelling_or_financial_need_notes: Stated income is from disability, indicating a compelling transportation need.
- final: summary_sentiment_analysis: User was responsive, cooperative, and clear; no signs of distress.
- at q1: reason_codes: DATA_INCOMPLETE

### F036 — truth `eligible` vs pred `ineligible`
- first divergence: q1 (truth `eligible`, pred `insufficient_information`)
- final: reason_codes: INSUFFICIENT_NOTICE
- final: outcome_notes: Request is ineligible due to insufficient minimum notice—user's appointment is in 3 days, volunteer flights require at least 5 business days' notice.
- final: summary_notes: User requested flight from Redding, CA to Sacramento, CA, for burn clinic follow-up, and is on SSDI. Is mobile, does not need in-flight medical monitoring, but the request is ineligible due to lack of minimum notice.
- final: service_region_rationale: Both Redding and Sacramento are within California, which is within AFW's service region as discussed.
- final: within_distance_limit_rationale: Redding to Sacramento is approximately 160 miles, which is within the 900 mile small-plane limit.
- final: minimum_notice_rationale: User reported appointment is in 3 days, which is less than the required minimum of 5 business days for a volunteer pilot flight.
- final: requires_small_plane_rationale: Typical routing within service region and distance is well suited to volunteer small-plane operation.
- final: requires_commercial_rationale: No mention or indication of commercial flight pathway; only small plane.
- final: is_mobile_rationale: User confirmed: 'I can walk and get around on my own.'
- final: is_medically_stable_rationale: User stated: 'I dont need medical monitoring on the flight.'
- final: financial_need_rationale: User stated they are on SSDI, which the agent notes shows financial need.
- final: summary_compelling_or_financial_need_notes: User is on SSDI, which qualifies as compelling financial need.
- final: summary_sentiment_analysis: User appeared factual and cooperative, repeatedly clarified information and restated needs, but expressed no overt frustration.
- at q1: reason_codes: DATA_INCOMPLETE

### F037 — truth `eligible` vs pred `ineligible`
- first divergence: q1 (truth `eligible`, pred `insufficient_information`)
- final: reason_codes: INSUFFICIENT_NOTICE
- final: outcome_notes: Ineligible due to insufficient notice; AFW requires at least five business days to arrange a volunteer pilot flight.
- final: summary_notes: User requested a flight from Stockton, CA to San Francisco, CA for a medical (MFM) appointment with only two days’ notice. They are mobile, medically stable, financially constrained, and may travel with spouse. Not a DV case. Referred to Air Care Alliance due to insufficient notice.
- final: service_region_rationale: Both Stockton, CA and San Francisco, CA are within AFW's service region (California).
- final: within_distance_limit_rationale: Stockton to San Francisco is significantly less than 900 miles and within the typical range for small-plane flights.
- final: minimum_notice_rationale: The user stated the appointment is in 2 days; AFW requires at least 5 business days' notice for volunteer pilot flights.
- final: requires_small_plane_rationale: Short in-state travel suitable for a small-plane flight by a volunteer pilot.
- final: requires_commercial_rationale: The chatbot did not indicate a commercial pathway; short route between two cities in California.
- final: is_mobile_rationale: User explicitly stated they can walk and get around on their own.
- final: is_medically_stable_rationale: User stated they do not require medical monitoring on the flight.
- final: is_pregnant_rationale: Pregnancy duration not specified, but agent did not flag ineligibility for this reason.
- final: summary_compelling_or_financial_need_notes: User cited one income as indicator of financial need.
- final: summary_sentiment_analysis: User was cooperative, straightforward, and focused on logistical needs; no notable distress or agitation.
- at q1: reason_codes: DATA_INCOMPLETE

### F038 — truth `eligible` vs pred `manual_review`
- first divergence: q1 (truth `eligible`, pred `insufficient_information`)
- final: reason_codes: EDGE_CASE_COMPLEX
- final: outcome_notes: Domestic violence relocation scenario with advocate assigned; routed for manual review for further processing.
- final: summary_notes: User requests DV shelter relocation flight from San Diego to Phoenix. Has shelter advocate, no funds, can walk, no medical monitoring needed, appointment in 11 days. Passenger number still pending.
- final: service_region_rationale: User stated travel is from San Diego, CA to Phoenix, AZ, which are both within AFW service region.
- final: within_distance_limit_rationale: San Diego to Phoenix is approximately 355 miles, well within the 900-mile small-plane limit.
- final: minimum_notice_rationale: User indicated appointment in 11 days, which exceeds the minimum notice requirement.
- final: requires_small_plane_rationale: Route is within regional and distance requirements for volunteer small-plane flights; both cities are accessible for AFW pilots.
- final: requires_commercial_rationale: No indication that commercial airline is needed; small-plane is appropriate.
- final: is_mobile_rationale: User stated 'I can walk and get around on my own.'
- final: is_medically_stable_rationale: User stated 'I dont need medical monitoring on the flight.'
- final: is_pregnant_rationale: No indication of pregnancy provided.
- final: summary_compelling_or_financial_need_notes: User stated 'on no funds,' indicating financial hardship and compelling need for assistance.
- final: summary_sentiment_analysis: User is direct, factual, and persistent but not emotional; demonstrates urgent need and clarity about situation.
- at q1: reason_codes: DATA_INCOMPLETE

### F039 — truth `eligible` vs pred `ineligible`
- first divergence: q1 (truth `eligible`, pred `ineligible`)
- final: reason_codes: DISTANCE_TOO_GREAT
- final: outcome_notes: The route between Tacoma and Seattle is well below AFW's minimum distance for a charitable flight.
- final: summary_notes: Caregiver for husband needing to travel from Tacoma to Seattle for chemo support. User is mobile, stable, experiencing financial hardship, but route is ineligible due to short distance.
- final: service_region_rationale: Agent identifies both Tacoma and Seattle as within AFW's service area (WA).
- final: within_distance_limit_rationale: Agent states that Tacoma and Seattle is 'well below our minimum distance for a charitable flight'.
- final: minimum_notice_rationale: Notice requirements are not a factor as the route is ineligible due to distance.
- final: requires_small_plane_rationale: Route is not eligible because it is too short for a flight, per agent explanation.
- final: requires_commercial_rationale: Route is not eligible because it is too short for a flight, per agent explanation.
- final: is_mobile_rationale: User indicated 'I can walk and get around on my own.'
- final: is_medically_stable_rationale: User stated 'I dont need medical monitoring on the flight.'
- final: is_pregnant_rationale: No pregnancy was discussed or indicated in the conversation.
- final: summary_compelling_or_financial_need_notes: User reported significant financial hardship in supporting husband’s chemotherapy.
- final: summary_sentiment_analysis: User appears stressed and in need, expressing hardship but remains cooperative.
- at q1: reason_codes: DISTANCE_TOO_GREAT

### F041 — truth `eligible` vs pred `manual_review`
- first divergence: q1 (truth `eligible`, pred `insufficient_information`)
- final: reason_codes: EDGE_CASE_COMPLEX,DATA_INCOMPLETE
- final: outcome_notes: Case sent to coordinator for review because it is unclear if the pediatric patient can sit upright with seat-belt.
- final: summary_notes: Caregiver requested flight for pediatric oncology for son, Modesto CA to Oakland CA, indicated financial need, confirmed not a DV case, meets minimum notice and mobility criteria for self, but it's unclear if son can sit with seat-belt—needs coordinator review.
- final: service_region_rationale: Both Modesto, CA and Oakland, CA are within Angel Flight West's service region as identified in the user's comments.
- final: within_distance_limit_rationale: The distance between Modesto and Oakland is well within 900 miles and suitable for small-plane travel.
- final: minimum_notice_rationale: User reports an appointment in 9 days, meeting the minimum notice requirement of 5 business days for a volunteer-pilot flight.
- final: requires_small_plane_rationale: The agent mentioned a 'free volunteer-pilot flight' suitable for this route and distance.
- final: requires_commercial_rationale: Commercial flight is not mentioned or indicated by the agent.
- final: is_mobile_rationale: User stated: 'I can walk and get around on my own.'
- final: is_medically_stable_rationale: User confirmed: 'I dont need medical monitoring on the flight.'
- final: is_pregnant_rationale: No pregnancy indicated in the conversation.
- final: summary_compelling_or_financial_need_notes: User indicated financial hardship by stating they are 'on farm wages.'
- final: summary_sentiment_analysis: User was clear, cooperative, and polite, demonstrating concern for meeting requirements and for son's medical needs.
- at q1: reason_codes: DATA_INCOMPLETE

