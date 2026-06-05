# Failure Analysis

## Run Summary
- personas: 120
- scored final outcomes: 120
- final outcome accuracy: 61.7%
- incorrect matches: 46
- unscored final outcomes: 0

## Error Concentration By Truth Class
- manual_review: 16 mismatches
- eligible: 13 mismatches
- insufficient_information: 11 mismatches
- ineligible: 6 mismatches

## Confusion Pairs
- truth `insufficient_information` predicted `manual_review`: 9
- truth `eligible` predicted `insufficient_information`: 8
- truth `manual_review` predicted `insufficient_information`: 7
- truth `manual_review` predicted `eligible`: 6
- truth `ineligible` predicted `insufficient_information`: 4
- truth `eligible` predicted `ineligible`: 4
- truth `manual_review` predicted `ineligible`: 3
- truth `ineligible` predicted `eligible`: 2
- truth `insufficient_information` predicted `ineligible`: 2
- truth `eligible` predicted `manual_review`: 1

## First Divergence Checkpoint
- q7: 37 mismatches
- q2: 35 mismatches
- q8: 35 mismatches
- q1: 34 mismatches
- q3: 34 mismatches
- q4: 34 mismatches
- q5: 34 mismatches
- q6: 31 mismatches

## Session Rationale — Outcome Reason Codes (failures only)
- `DATA_INCOMPLETE`: 28
- `DISTANCE_TOO_GREAT`: 3
- `INSUFFICIENT_NOTICE`: 2
- `REASON_FOR_TRAVEL_NOT_ELIGIBLE`: 2
- `DATA_INCOMPLETE,INSUFFICIENT_NOTICE`: 1
- `OUT_OF_SERVICE_REGION,OTHER`: 1
- `DISTANCE_TOO_GREAT,OUT_OF_SERVICE_REGION`: 1

## Session Rationale — Final outcome_notes (failures only)
- (1x) Eligibility not determined due to missing exact travel date; minimum notice cannot be confirmed.
- (1x) User has not yet provided an exact travel date; screening cannot be fully completed.
- (1x) Screening nearly complete; user has not yet answered about previous ticket usage this calendar year.
- (1x) User meets criteria for volunteer pilot flight: medical need, financial hardship, mobility, advance notice, within service region and distance limits.
- (1x) User has not completed all screening questions regarding mobility and whether more than one person is traveling.
- (1x) User meets eligibility for small-plane volunteer flight: in-region, within distance, mobile, medically stable, sufficient notice.
- (1x) Screening is in progress; agent requested info about travel companions. Final eligibility determination not yet reached.
- (1x) Agent needs to confirm appointment date to determine if minimum notice is met and begin medical stability screening.

## Session Rationale — Criterion fields cited on failures
- (3x) dv_context_rationale: User stated 'Not a domestic violence case.'
- (3x) dv_context_rationale: User explicitly stated 'Not a domestic violence case.'
- (2x) dv_in_shelter_rationale: Not applicable; user denied DV context.
- (2x) dv_provider_rationale: Not applicable; user denied DV context.
- (2x) dv_context_rationale: No mention of domestic violence context.
- (2x) is_mobile_rationale: User stated: 'I can walk and get around on my own.'
- (2x) dv_in_shelter_rationale: No indication user is in a DV shelter.
- (2x) is_mobile_rationale: User confirmed they can walk and transfer without help.
- (2x) dv_context_rationale: User explicitly stated: 'Not a domestic violence case.'
- (2x) dv_in_shelter_rationale: Not a DV case.
- (2x) dv_provider_rationale: Not a DV case.
- (2x) dv_context_rationale: User explicitly stated this is not a domestic violence case.

## Rationale Evidence By Confusion Pattern
### truth `insufficient_information` → predicted `manual_review`
- F061: reason_codes: DATA_INCOMPLETE | outcome_notes: Trip purpose, origin, destination, and other key info not provided; coordinator follow-up needed. | summary_notes: User asked about help with a flight but did not specify reason for travel, cities, or dates. Unclear if DV or medical context. User may have mobility challenges.
- F061 @ q5: reason_codes: DATA_INCOMPLETE
- F061 @ q5: outcome_notes: Trip purpose, origin, destination, and other key info not provided; coordinator follow-up needed.
- F061 @ q5: summary_notes: User asked about help with a flight but did not specify reason for travel, cities, or dates. Unclear if DV or medical context. User may have mobility challenges.
### truth `eligible` → predicted `insufficient_information`
- F031: reason_codes: DATA_INCOMPLETE | outcome_notes: Screening is in progress; agent requested info about travel companions. Final eligibility determination not yet reached. | summary_notes: User seeks transport from Fresno, CA to Los Angeles, CA for cancer treatment at UCLA; can walk independently, needs travel in 10 days, has financial hardship, no medical monitoring needed.
- F031 @ q1: reason_codes: DATA_INCOMPLETE
- F031 @ q1: outcome_notes: The agent has not yet received a travel/appointment date from the user to fully determine eligibility.
- F031 @ q1: summary_notes: User requested flight from Fresno, CA to UCLA in Los Angeles, CA for cancer treatment; unable to afford travel; agent requested appointment date.
### truth `manual_review` → predicted `insufficient_information`
- F096: reason_codes: DATA_INCOMPLETE | outcome_notes: Chatbot is still in the process of confirming in-flight medical needs before eligibility outcome. | summary_notes: User requests a flight from Carson City, NV to Sacramento, CA in about 9 days for cardiology, reports independent mobility, has financial need, and is not a DV case. Awaiting response regarding in-flight medical needs before completing screening.
- F096 @ q1: reason_codes: DATA_INCOMPLETE
- F096 @ q1: outcome_notes: User has not yet provided specific travel date; screening incomplete.
- F096 @ q1: summary_notes: User requested transportation from Carson City, NV to Sacramento, CA for a cardiology appointment in about 9 days but has not provided exact travel date yet.
### truth `manual_review` → predicted `eligible`
- F097: outcome_notes: User meets criteria for a volunteer-pilot flight: appropriate distance, advance notice, medical stability, mobility, and compelling need. | summary_notes: User inquired about travel from Idaho Falls, ID to Seattle, WA for MS clinic in 14 days. They confirmed ability to transfer/walk independently, have manageable panic, no DV context, and cited rural hardship. Agent indicated eligibility and directed user to application. | service_region_rationale: Both Idaho and Washington are within AFW’s service region. User specified Idaho Falls, ID to Seattle, WA.
- F097 @ q1: reason_codes: DATA_INCOMPLETE
- F097 @ q1: outcome_notes: The agent is still mid-screening and awaiting answers on medical stability and mobility criteria.
- F097 @ q1: summary_notes: User requested flight from Idaho Falls, ID to Seattle, WA for MS clinic in about 14 days. Agent is screening for mobility and in-flight medical needs.
### truth `ineligible` → predicted `insufficient_information`
- F015: reason_codes: DATA_INCOMPLETE,INSUFFICIENT_NOTICE | outcome_notes: Eligibility not determined due to missing exact travel date; minimum notice cannot be confirmed. | summary_notes: User seeks help flying from Honolulu to San Francisco for mainland specialist medical treatment, reports no travel funds, and is requesting for self and one companion. No domestic violence context. Did not provide an exact travel date.
- F015 @ q1: reason_codes: DATA_INCOMPLETE,INSUFFICIENT_NOTICE
- F015 @ q1: outcome_notes: Key information missing on mobility, medical stability, and financial hardship; date does not meet minimum notice.
- F015 @ q1: summary_notes: User requested transportation from Honolulu, HI to San Francisco, CA for medical appointment with a mainland specialist. Specific date requested is Monday (one day from now).
### truth `eligible` → predicted `ineligible`
- F036: reason_codes: INSUFFICIENT_NOTICE | outcome_notes: Ineligible for this trip because minimum notice requirement (5 business days) for volunteer pilot pathway was not met. | summary_notes: User requested a flight from Redding to Sacramento, CA for burn clinic follow-up in 3 days. User is on SSDI, mobile, and stable, but notice requirement could not be met. Referred to Air Care Alliance.
- F036 @ q1: reason_codes: DATA_INCOMPLETE
- F036 @ q1: outcome_notes: Insufficient information: appointment/travel date, mobility, medical stability not yet provided.
- F036 @ q1: summary_notes: User requested a volunteer flight from Redding to Sacramento for a burn clinic follow-up. Financial need noted (SSDI), further details required.

## Incorrect Personas (with session rationale)
### F015 — truth `ineligible` vs pred `insufficient_information`
- first divergence: q1 (truth `eligible`, pred `insufficient_information`)
- final: reason_codes: DATA_INCOMPLETE,INSUFFICIENT_NOTICE
- final: outcome_notes: Eligibility not determined due to missing exact travel date; minimum notice cannot be confirmed.
- final: summary_notes: User seeks help flying from Honolulu to San Francisco for mainland specialist medical treatment, reports no travel funds, and is requesting for self and one companion. No domestic violence context. Did not provide an exact travel date.
- final: service_region_rationale: Both Honolulu, HI and San Francisco, CA are within or connected to AFW's service region.
- final: within_distance_limit_rationale: Distance between Honolulu and San Francisco (~2400 miles) exceeds the 900 mile limit for volunteer small plane flights.
- final: minimum_notice_rationale: Exact date was not provided; unable to confirm if minimum notice can be met.
- final: requires_small_plane_rationale: Route is far too long for a volunteer small plane.
- final: requires_commercial_rationale: Route from Honolulu to San Francisco requires commercial airline travel (Alaska Airlines partner).
- final: is_mobile_rationale: User replied 'ok on planes', suggesting sufficient mobility for air travel.
- final: is_medically_stable_rationale: User did not report need for monitoring and no instability was mentioned.
- final: is_pregnant_rationale: No pregnancy or pregnancy risk was mentioned.
- final: summary_compelling_or_financial_need_notes: User has no funds for travel.
- final: summary_sentiment_analysis: User is responsive and direct, providing information as requested; sentiment appears neutral.
- at q1: reason_codes: DATA_INCOMPLETE,INSUFFICIENT_NOTICE
- at q1: outcome_notes: Key information missing on mobility, medical stability, and financial hardship; date does not meet minimum notice.
- at q1: summary_notes: User requested transportation from Honolulu, HI to San Francisco, CA for medical appointment with a mainland specialist. Specific date requested is Monday (one day from now).
- at q1: service_region_rationale: User stated origin is Honolulu, HI and destination is San Francisco, CA, both within AFW's service region.
- at q1: within_distance_limit_rationale: The trip is approximately 2400 miles, which exceeds the typical small-plane limit.
- at q1: minimum_notice_rationale: The user requested travel 'Monday' and the chat took place the day before, which does not meet minimum required notice.
- at q1: requires_small_plane_rationale: Distance and overwater flight make small-plane inappropriate.
- at q1: requires_commercial_rationale: Route is inter-island and over 900 miles; appropriate for commercial partner pathway.
- at q1: summary_compelling_or_financial_need_notes: Financial need not discussed.
- at q1: summary_sentiment_analysis: User was direct and concise in their responses.

### F021 — truth `ineligible` vs pred `insufficient_information`
- first divergence: q1 (truth `eligible`, pred `insufficient_information`)
- final: reason_codes: DATA_INCOMPLETE
- final: outcome_notes: User has not yet provided an exact travel date; screening cannot be fully completed.
- final: summary_notes: User requested flight from Bakersfield to Los Angeles for 13-day epilepsy monitoring. Confirmed ability to walk independently. Awaiting exact travel date.
- final: service_region_rationale: Both Bakersfield, CA and Los Angeles, CA are within Angel Flight West's service region (CA).
- final: within_distance_limit_rationale: Bakersfield to Los Angeles is approximately 110 miles, well within the 900-mile small-plane limit.
- final: minimum_notice_rationale: User indicated travel in 13 days, which is greater than the minimum notice needed for a volunteer pilot flight.
- final: requires_small_plane_rationale: Short route within the AFW region, typically handled by volunteer pilots.
- final: requires_commercial_rationale: No indication that a commercial flight pathway is required; route suitable for small-plane.
- final: is_mobile_rationale: User stated they can walk on their own.
- final: is_medically_stable_rationale: User is seeking non-emergency epilepsy monitoring and implied ability to walk independently.
- final: is_pregnant_rationale: No pregnancy was mentioned.
- final: summary_compelling_or_financial_need_notes: User is seeking no-cost medical transport, suggesting financial/transportation need.
- final: summary_sentiment_analysis: User was cooperative, direct, and clear with responses.
- at q1: reason_codes: DATA_INCOMPLETE
- at q1: outcome_notes: Screening incomplete—the chatbot is still collecting the travel date and other details.
- at q1: summary_notes: User inquiring about flight from Bakersfield, CA to Los Angeles, CA for epilepsy monitoring unit; travel date and eligibility details still being collected.
- at q1: service_region_rationale: User stated travel is from Bakersfield CA to Los Angeles CA, both within Angel Flight West's service region.
- at q1: within_distance_limit_rationale: The distance between Bakersfield and Los Angeles (~110 miles) is within the small plane limit.
- at q1: minimum_notice_rationale: No travel date was provided yet, so minimum notice cannot be determined.
- at q1: requires_small_plane_rationale: The chatbot is pursuing the small plane volunteer pathway based on distance and region.
- at q1: requires_commercial_rationale: The chatbot did not indicate a need for commercial pathway.
- at q1: summary_compelling_or_financial_need_notes: No financial or compelling need stated yet.
- at q1: summary_sentiment_analysis: User appears straightforward, focused on gathering travel assistance information.

### F024 — truth `ineligible` vs pred `insufficient_information`
- first divergence: q1 (truth `eligible`, pred `insufficient_information`)
- final: reason_codes: DATA_INCOMPLETE
- final: outcome_notes: Screening nearly complete; user has not yet answered about previous ticket usage this calendar year.
- final: summary_notes: User requests assistance for four airline tickets (Anchorage to Seattle) for ongoing chemo treatment, with stable condition and adequate notice. No DV context. Not all prior ticket use info gathered yet.
- final: service_region_rationale: User requested travel from Anchorage, AK to Seattle, WA. Both locations are within Angel Flight West's service region or reachable by commercial partner.
- final: within_distance_limit_rationale: Distance between Anchorage and Seattle is above the typical 900-mile small plane threshold, so commercial pathway is relevant.
- final: minimum_notice_rationale: User specified that travel is needed in about 10 days, which meets the minimum notice for commercial pathway (≥2 business days).
- final: requires_small_plane_rationale: Distance is above limit for small planes; commercial airline is required for Anchorage to Seattle.
- final: requires_commercial_rationale: Travel between Anchorage and Seattle fits commercial airline pathway per agent screening.
- final: is_mobile_rationale: User confirmed all passengers can use regular airline seats; 'Airline ok' and confirmed stable.
- final: is_medically_stable_rationale: User responded 'Stable' and denied need for in-flight medical care or monitoring.
- final: is_pregnant_rationale: No pregnancy indicated or discussed.
- final: summary_compelling_or_financial_need_notes: User asked about Alaska ticket costs, reflecting financial hardship for air travel related to treatment.
- final: summary_sentiment_analysis: Neutral, matter-of-fact tone; responsive to questions, appears in need of help but not emotional.
- at q1: reason_codes: DATA_INCOMPLETE
- at q1: outcome_notes: Awaiting user's travel date before eligibility or next step can be determined.
- at q1: summary_notes: User requests flight from Anchorage, AK to Seattle, WA for four tickets for ongoing chemotherapy. Agent is awaiting further details (travel date) to proceed.
- at q1: service_region_rationale: Both Anchorage, AK and Seattle, WA are within or reachable from AFW's service region as per user's provided cities and states.
- at q1: within_distance_limit_rationale: The approximate distance between Anchorage and Seattle is 1440 miles, which exceeds the 900-mile limit for small plane volunteer flights.
- at q1: minimum_notice_rationale: Travel date has not yet been provided by the user, so notice could not be evaluated.
- at q1: requires_small_plane_rationale: The distance between Anchorage and Seattle is too great for volunteer pilot small-plane service.
- at q1: requires_commercial_rationale: Routes between Anchorage and Seattle are typically served by Alaska Airlines, AFW's commercial partner.
- at q1: summary_compelling_or_financial_need_notes: Travel for repeated cancer treatment is a compelling need; user is requesting free transport.
- at q1: summary_sentiment_analysis: User communicated clear and factual information; tone is neutral and focused on the medical need.

### F025 — truth `ineligible` vs pred `eligible`
- first divergence: q1 (truth `eligible`, pred `insufficient_information`)
- final: outcome_notes: User meets criteria for volunteer pilot flight: medical need, financial hardship, mobility, advance notice, within service region and distance limits.
- final: summary_notes: User requesting flight for three people from Fresno to Los Angeles for radiation treatment in 14 days. All passengers mobile and stable. Unable to pay for alternative transport. Agent confirmed eligibility and directed to application form.
- final: service_region_rationale: Both Fresno and Los Angeles are in California, which is within AFW's service region.
- final: within_distance_limit_rationale: Agent assessed Fresno to Los Angeles is within single-leg distance for a volunteer pilot (≈220 miles).
- final: minimum_notice_rationale: User requested flight in 14 days, which is more than 5 business days notice required for volunteer pilot pathway.
- final: requires_small_plane_rationale: Agent determined trip is short enough and suitable for a volunteer pilot/GA small plane based on distance and service region.
- final: requires_commercial_rationale: Agent did not indicate commercial airline pathway; only small plane volunteer-pilot flights discussed.
- final: is_mobile_rationale: User said 'Walks fine' when asked if the patient could step up into the plane and sit with a seatbelt.
- final: is_medically_stable_rationale: User said 'Stable' in response to questions about the patient's condition.
- final: is_pregnant_rationale: No mention or suggestion of pregnancy; not applicable per conversation.
- final: summary_compelling_or_financial_need_notes: User reported inability to pay for commercial airfare or ground transport.
- final: summary_sentiment_analysis: User was direct, cooperative, and responsive throughout the screening. No negative sentiment noted.
- at q1: reason_codes: DATA_INCOMPLETE
- at q1: outcome_notes: Key screening detail (minimum notice for travel date, mobility, financial need) not yet obtained.
- at q1: summary_notes: User requested help for travel from Fresno to Los Angeles for radiation for three companions in about 14 days. Chatbot is gathering minimum notice and additional criteria.
- at q1: service_region_rationale: User specified both origin (Fresno, CA) and destination (Los Angeles, CA) within CA, which is in the AFW service region.
- at q1: within_distance_limit_rationale: Approximate distance Fresno-Los Angeles is about 220 miles, within 900-mile small plane limit.
- at q1: minimum_notice_rationale: Chatbot is explicitly checking if the first needed flight is at least five business days from today, so the minimum notice is not yet confirmed.
- at q1: requires_small_plane_rationale: In-state trip of 220 miles is suitable for small plane volunteer pilot.
- at q1: requires_commercial_rationale: Commercial travel pathway is not indicated.
- at q1: summary_compelling_or_financial_need_notes: No compelling or financial need discussed yet.
- at q1: summary_sentiment_analysis: User is straightforward and responsive, providing reason for travel and timing. Tone is neutral and direct.

### F026 — truth `ineligible` vs pred `insufficient_information`
- first divergence: q1 (truth `eligible`, pred `insufficient_information`)
- final: reason_codes: DATA_INCOMPLETE
- final: outcome_notes: User has not completed all screening questions regarding mobility and whether more than one person is traveling.
- final: summary_notes: User requested help flying from Modesto to San Francisco as a caregiver for a father receiving chemo. The user is mobile, medically stable, not a DV case, has financial need (disability income), and wishes to travel in 11 days. The agent is still confirming final details on eligibility.
- final: service_region_rationale: Both Modesto and San Francisco are in California, which is within AFW's service region. The user explicitly stated both cities.
- final: within_distance_limit_rationale: The distance from Modesto to San Francisco is approximately 90 miles, which is well within the 900 mile limit for small plane flights.
- final: minimum_notice_rationale: The user reports travel is about 11 days away, which meets the minimum notice requirements for a volunteer pilot flown flight (at least 5 business days).
- final: requires_small_plane_rationale: The short, intrastate route (Modesto to San Francisco, 90 miles) is suitable for a small-plane volunteer pilot, per AFW guidelines.
- final: requires_commercial_rationale: Commercial is not required for this route; small-plane volunteer pilot is appropriate.
- final: is_mobile_rationale: User confirmed being 'Mobile.' Agent repeatedly asked and user confirmed mobility.
- final: is_medically_stable_rationale: User confirmed being 'Stable.'
- final: is_pregnant_rationale: No indication of pregnancy provided or suggested.
- final: summary_compelling_or_financial_need_notes: User stated their income is from disability, indicating financial need.
- final: summary_sentiment_analysis: User was cooperative and informative throughout the conversation, straightforward and responsive.
- at q1: reason_codes: DATA_INCOMPLETE
- at q1: outcome_notes: Eligibility pending--mobility criteria not yet confirmed. Agent is in the process of screening.
- at q1: summary_notes: User is a caregiver traveling from Modesto, CA to San Francisco, CA to support father during chemotherapy. Trip is planned for approximately 11 days from now. Screening for mobility is in progress.
- at q1: service_region_rationale: Both Modesto and San Francisco are in California, which is within the AFW service region. User listed both cities explicitly.
- at q1: within_distance_limit_rationale: The Modesto to San Francisco route is about 85 miles, well within the 900-mile limit for small-plane flights.
- at q1: minimum_notice_rationale: User indicated travel is approximately 11 days from today, which exceeds the 5-business day minimum for volunteer pilot flights.
- at q1: requires_small_plane_rationale: Short in-state travel from Modesto to San Francisco fits criteria for volunteer pilot flight.
- at q1: requires_commercial_rationale: Commercial flight is not needed for short in-state travel between origin and destination.
- at q1: summary_compelling_or_financial_need_notes: No financial or compelling need information yet supplied.
- at q1: summary_sentiment_analysis: User appears focused and informative, responds clearly to screening questions.

### F027 — truth `ineligible` vs pred `eligible`
- first divergence: q1 (truth `eligible`, pred `insufficient_information`)
- final: outcome_notes: User meets eligibility for small-plane volunteer flight: in-region, within distance, mobile, medically stable, sufficient notice.
- final: summary_notes: User requests transportation from San Jose to Sacramento for cardiology follow-up. Traveling solo, mobile, and medically stable. Requests flight in approx. 9 days; not a DV case.
- final: service_region_rationale: Both San Jose and Sacramento are within California, which is in AFW's service region; user stated 'san jose california to sacramento california'.
- final: within_distance_limit_rationale: San Jose to Sacramento is well under the 900-mile small plane distance limit (approx. 90 miles).
- final: minimum_notice_rationale: User requested flight in 'around 9 days', which meets the 5 business day minimum for volunteer-flown flights.
- final: requires_small_plane_rationale: Trip is between two cities in CA, well within distance for a small plane. No commercial partner required for such a short flight.
- final: requires_commercial_rationale: User inquired about paying for Southwest, but the distance and scenario best fit small-plane volunteer flight as per AFW standard screening.
- final: is_mobile_rationale: User confirmed 'fine' when asked about walking, seating, and transferring unassisted in small plane.
- final: is_medically_stable_rationale: User stated 'stable' when asked about medical stability for non-emergency travel.
- final: is_pregnant_rationale: No indication or mention of pregnancy; nothing in chat to suggest otherwise.
- final: summary_compelling_or_financial_need_notes: Although user said they can afford Southwest, continued with AFW screening, indicating a compelling need for assistance.
- final: summary_sentiment_analysis: User is cooperative, concise, direct, and responsive. No distress or frustration displayed.
- at q1: reason_codes: DATA_INCOMPLETE
- at q1: outcome_notes: Eligibility screening is incomplete—awaiting user's response on mobility and medical stability questions.
- at q1: summary_notes: User requested help traveling from San Jose to Sacramento for a cardiology follow-up in 9 days and reports financial need. Screening of mobility and medical stability is in progress.
- at q1: service_region_rationale: Both San Jose and Sacramento are in California, which is within the AFW service region.
- at q1: within_distance_limit_rationale: Distance between San Jose and Sacramento is well within the small-plane limit of 900 miles.
- at q1: minimum_notice_rationale: The user wants to travel in 9 days, which exceeds the 5 business day minimum notice for volunteer pilots.
- at q1: requires_small_plane_rationale: Route distance and in-region travel is appropriate for small-plane volunteer pathway.
- at q1: requires_commercial_rationale: Commercial airline is not indicated for this short, in-region trip.
- at q1: summary_compelling_or_financial_need_notes: User reports inability to afford a flight.
- at q1: summary_sentiment_analysis: User seems motivated and in need, seeking help in a straightforward and neutral tone.

### F031 — truth `eligible` vs pred `insufficient_information`
- first divergence: q1 (truth `eligible`, pred `insufficient_information`)
- final: reason_codes: DATA_INCOMPLETE
- final: outcome_notes: Screening is in progress; agent requested info about travel companions. Final eligibility determination not yet reached.
- final: summary_notes: User seeks transport from Fresno, CA to Los Angeles, CA for cancer treatment at UCLA; can walk independently, needs travel in 10 days, has financial hardship, no medical monitoring needed.
- final: service_region_rationale: Both Fresno, CA and Los Angeles, CA are within Angel Flight West's service region (CA). User identified both cities explicitly.
- final: within_distance_limit_rationale: The distance between Fresno and Los Angeles is approximately 220 miles, within the typical 900 mile limit for a small plane.
- final: minimum_notice_rationale: User stated their appointment is in 10 days, which is more than 5 business days minimum for a volunteer pilot flight.
- final: requires_small_plane_rationale: The route is within the small plane range and fits the model for a volunteer pilot flight; agent is screening for this pathway.
- final: requires_commercial_rationale: No indication of commercial flight eligibility; route is well within small plane distance and in-region.
- final: is_mobile_rationale: User says they can walk and get around on their own.
- final: is_medically_stable_rationale: User confirmed they do not need medical monitoring during the flight.
- final: is_pregnant_rationale: No mention or indication of pregnancy; no relevant comments.
- final: summary_compelling_or_financial_need_notes: User is on disability and unable to afford transportation.
- final: summary_sentiment_analysis: User appears cooperative, factual, and calm in their responses.
- at q1: reason_codes: DATA_INCOMPLETE
- at q1: outcome_notes: The agent has not yet received a travel/appointment date from the user to fully determine eligibility.
- at q1: summary_notes: User requested flight from Fresno, CA to UCLA in Los Angeles, CA for cancer treatment; unable to afford travel; agent requested appointment date.
- at q1: service_region_rationale: Both Fresno, CA and Los Angeles, CA are within AFW's service region (CA). User specified both origin and destination clearly.
- at q1: within_distance_limit_rationale: Fresno to Los Angeles is approximately 220 miles, well within 900-mile limit for small-plane flights.
- at q1: minimum_notice_rationale: The user has not provided a specific travel/appointment date, so minimum notice cannot be determined yet.
- at q1: requires_small_plane_rationale: The route within California, under 900 miles, aligns with typical small-plane volunteer pilot missions as implied by agent's comments.
- at q1: requires_commercial_rationale: There is no indication a commercial flight is required; small-plane is the presumed pathway per agent.
- at q1: summary_compelling_or_financial_need_notes: User is on disability and cannot afford travel costs.
- at q1: summary_sentiment_analysis: User appears direct, focused on seeking assistance for important medical needs; tone is clear but neutral.

### F032 — truth `eligible` vs pred `insufficient_information`
- first divergence: none (truth ``, pred ``)
- final: reason_codes: DATA_INCOMPLETE
- final: outcome_notes: Agent needs to confirm appointment date to determine if minimum notice is met and begin medical stability screening.
- final: summary_notes: User seeking flight from Reno, NV to San Francisco, CA for pre-transplant evaluation at UCSF, cited Medicaid and financial hardship. Agent began minimum notice screening, conversation incomplete.
- final: service_region_rationale: User's origin (Reno, NV) and destination (San Francisco, CA) are both within the AFW service region as stated by the user.
- final: within_distance_limit_rationale: Reno, NV to San Francisco, CA is approximately 218 miles, within the small-plane limit; agent is proceeding with screening.
- final: minimum_notice_rationale: Agent is currently verifying if the appointment is at least five business days from today, as this is the minimum notice required for a small-plane (volunteer pilot) flight.
- final: requires_small_plane_rationale: Reno, NV to San Francisco, CA is within typical small plane range. Agent asked about timing in accordance with volunteer pilot pathway.
- final: requires_commercial_rationale: Not addressed; routing appears to be for small-plane volunteer pilots.
- final: is_mobile_rationale: Not determined in conversation so far.
- final: is_medically_stable_rationale: Not addressed yet in conversation.
- final: is_pregnant_rationale: Not addressed yet in conversation.
- final: summary_compelling_or_financial_need_notes: User stated they are on Medicaid, with insurance gaps.
- final: summary_sentiment_analysis: User is direct, focused on logistics, and expresses clear need for assistance with transportation for a medical appointment.

### F033 — truth `eligible` vs pred `insufficient_information`
- first divergence: q1 (truth `eligible`, pred `insufficient_information`)
- final: reason_codes: DATA_INCOMPLETE
- final: outcome_notes: Screening incomplete—agent is waiting for appointment date to verify minimum notice.
- final: summary_notes: User needs weekly travel from Eugene, OR to Portland, OR for OHSU infusions, on fixed income. Not a DV case. Appointment date information still needed.
- final: service_region_rationale: Both Eugene, OR and Portland, OR are within Angel Flight West's service region as specified.
- final: within_distance_limit_rationale: The distance from Eugene to Portland is approximately 110 miles, well within the 900 mile limit for small planes.
- final: minimum_notice_rationale: The chatbot has not yet determined the appointment date or whether minimum notice is met; user has not provided a date.
- final: requires_small_plane_rationale: Travel is within distance for volunteer pilot flight and both cities are accessible via GA airports.
- final: requires_commercial_rationale: No indication from the agent that commercial air is required.
- final: is_mobile_rationale: The user did not indicate mobility limitations and is not a DV client.
- final: is_medically_stable_rationale: No concerns about medical stability have been raised in the conversation so far.
- final: is_pregnant_rationale: There is no mention of pregnancy.
- final: summary_compelling_or_financial_need_notes: User is on fixed income and likely cannot afford commercial travel.
- final: summary_sentiment_analysis: User is matter-of-fact, neutral, seeking help, and responsive.
- at q1: reason_codes: DATA_INCOMPLETE
- at q1: outcome_notes: Minimum notice unconfirmed. Still gathering details regarding mobility and medical stability.
- at q1: summary_notes: User is seeking help with weekly travel from Eugene, OR to Portland, OR for OHSU infusions, citing financial need. Minimum notice and further details are pending.
- at q1: service_region_rationale: Both Eugene, OR and Portland, OR are within AFW's service region (Oregon). User explicitly gave these as origin and destination.
- at q1: within_distance_limit_rationale: The route Eugene to Portland is approximately 110 miles, well within the 900-mile limit for small plane flights.
- at q1: minimum_notice_rationale: Chatbot is clarifying if the next infusion appointment is at least 5 business days away; user has not confirmed. Minimum notice requirement currently unconfirmed.
- at q1: requires_small_plane_rationale: This is an in-region, short-distance route appropriate for volunteer-pilot small-plane service as per AFW standards.
- at q1: requires_commercial_rationale: Route is within small-plane distance, intrastate, so commercial airline is not required.
- at q1: summary_compelling_or_financial_need_notes: User reports being on a fixed income.
- at q1: summary_sentiment_analysis: User seems matter-of-fact and motivated by need; no distress or frustration noted.

### F034 — truth `eligible` vs pred `insufficient_information`
- first divergence: q1 (truth `eligible`, pred `insufficient_information`)
- final: reason_codes: DATA_INCOMPLETE
- final: outcome_notes: User did not yet provide a travel date; cannot assess minimum notice or finalize eligibility.
- final: summary_notes: User seeking flight from Boise, ID to Salt Lake City, UT for orthopedic follow up. Route is within region and distance limits, and user cited rural transportation barrier. No travel date provided yet. Not a DV case.
- final: service_region_rationale: User stated origin is Boise, ID and destination is Salt Lake City, UT, both within Angel Flight West service region.
- final: within_distance_limit_rationale: Boise, ID to Salt Lake City, UT is approximately 296 miles, which is within the 900 mile limit for small planes.
- final: minimum_notice_rationale: No travel date provided yet; minimum notice can't be assessed until date is given.
- final: requires_small_plane_rationale: Distance and route are typical for volunteer pilot flights within service area; agent referenced rural barriers.
- final: requires_commercial_rationale: No indication that commercial flight pathway is required based on user input.
- final: is_mobile_rationale: No comments in conversation suggesting mobility issues; patient self-identifies for orthopedic follow up only.
- final: is_medically_stable_rationale: No comments indicating instability; seeking routine orthopedic follow up suggests medical stability.
- final: is_pregnant_rationale: No mention of pregnancy.
- final: summary_compelling_or_financial_need_notes: Rural/transportation barrier noted as compelling need.
- final: summary_sentiment_analysis: User is factual and cooperative, responding directly to screening questions.
- at q1: reason_codes: DATA_INCOMPLETE
- at q1: outcome_notes: Incomplete data: user's travel/appointment date and mobility and medical stability have not yet been established.
- at q1: summary_notes: User from Boise, ID seeking assistance traveling to Salt Lake City, UT for orthopedic follow-up. Reports rural barrier. Has not yet provided appointment date or information on mobility or medical stability.
- at q1: service_region_rationale: Both Boise, ID and Salt Lake City, UT are within AFW's service region as identified from user comments.
- at q1: within_distance_limit_rationale: Boise, ID to Salt Lake City, UT is approximately 340 miles, within the ≤900 mile limit for volunteer pilots.
- at q1: minimum_notice_rationale: Minimum notice cannot be determined because the user has not yet provided their appointment or travel date.
- at q1: requires_small_plane_rationale: Volunteer pilot pathway is appropriate due to trip distance and cities listed.
- at q1: requires_commercial_rationale: Commercial pathway is not indicated without evidence of excessive distance or lack of volunteer pilot availability.
- at q1: summary_compelling_or_financial_need_notes: User reports a rural barrier, indicating lack of access to transportation resources.
- at q1: summary_sentiment_analysis: User appears direct and focused on obtaining transportation for medical needs.

### F036 — truth `eligible` vs pred `ineligible`
- first divergence: q1 (truth `eligible`, pred `insufficient_information`)
- final: reason_codes: INSUFFICIENT_NOTICE
- final: outcome_notes: Ineligible for this trip because minimum notice requirement (5 business days) for volunteer pilot pathway was not met.
- final: summary_notes: User requested a flight from Redding to Sacramento, CA for burn clinic follow-up in 3 days. User is on SSDI, mobile, and stable, but notice requirement could not be met. Referred to Air Care Alliance.
- final: service_region_rationale: Both Redding, CA and Sacramento, CA are within AFW's service region as per user's stated route.
- final: within_distance_limit_rationale: Redding to Sacramento is approximately 160 miles, well within small-plane distance limits.
- final: minimum_notice_rationale: User stated their appointment is in 3 days and agent said 5 business days minimum notice is required.
- final: requires_small_plane_rationale: User is seeking help for an in-state, short distance medical flight; agent assessed for volunteer pilot pathway.
- final: requires_commercial_rationale: No indication that commercial flight is required or considered for this short, intra-state route.
- final: is_mobile_rationale: User stated: 'I can walk and get around on my own.'
- final: is_medically_stable_rationale: User stated: 'I dont need medical monitoring on the flight.'
- final: financial_need_rationale: User is on SSDI; agent confirmed this satisfies the financial need guideline.
- final: summary_compelling_or_financial_need_notes: User indicated SSDI as income; financial need confirmed by agent.
- final: summary_sentiment_analysis: User was forthright and factual in providing details and responded politely to disqualification.
- at q1: reason_codes: DATA_INCOMPLETE
- at q1: outcome_notes: Insufficient information: appointment/travel date, mobility, medical stability not yet provided.
- at q1: summary_notes: User requested a volunteer flight from Redding to Sacramento for a burn clinic follow-up. Financial need noted (SSDI), further details required.
- at q1: service_region_rationale: User requested a flight from Redding, CA to Sacramento, CA, both of which are in AFW's service region (CA).
- at q1: within_distance_limit_rationale: Redding to Sacramento is approximately 160 miles, well within the typical small-plane distance limit (<=900 miles).
- at q1: minimum_notice_rationale: Chatbot is still collecting information about appointment date to assess if notice requirements are met.
- at q1: requires_small_plane_rationale: Redding to Sacramento is within AFW's service region and typical for volunteer pilot flights.
- at q1: requires_commercial_rationale: No indication that commercial flight is required for this route.
- at q1: summary_compelling_or_financial_need_notes: User is on SSDI, suggesting financial hardship.
- at q1: summary_sentiment_analysis: User is direct and focused on arranging medical travel, no distress noted.

### F037 — truth `eligible` vs pred `ineligible`
- first divergence: q1 (truth `eligible`, pred `insufficient_information`)
- final: reason_codes: INSUFFICIENT_NOTICE
- final: outcome_notes: Request is ineligible due to insufficient notice; Angel Flight West requires at least 5 business days for volunteer flights.
- final: summary_notes: User requested flight from Stockton to San Francisco for an MFM (pregnancy) appointment, is on one income, can walk independently, and needs travel in 2 days. Agent explained AFW cannot assist on short notice and provided alternative resources (Air Care Alliance, social services).
- final: service_region_rationale: Both Stockton, CA and San Francisco, CA are within AFW's service region as both cities are located in California.
- final: within_distance_limit_rationale: Stockton to San Francisco is significantly less than 900 miles, within the volunteer pilot small-plane range.
- final: minimum_notice_rationale: The user reported the appointment is in 2 days; volunteer pilot pathway requires 5 business days notice.
- final: requires_small_plane_rationale: Stockton to San Francisco is a typical short route for volunteer small-plane travel within region.
- final: requires_commercial_rationale: Not indicated; commercial option not discussed by chatbot.
- final: is_mobile_rationale: User stated 'I can walk and get around on my own.'
- final: is_medically_stable_rationale: User reported no need for medical monitoring on flight and gave no indication of instability.
- final: is_pregnant_rationale: User referenced MFM (Maternal-Fetal Medicine) appointment, consistent with pregnancy; no indication of gestational age or high-risk status provided.
- final: summary_compelling_or_financial_need_notes: User reported they are on one income, reflecting financial hardship.
- final: summary_sentiment_analysis: User communicated need directly and politely; interaction was clear and cooperative but demonstrated concern regarding transportation barriers.
- at q1: reason_codes: DATA_INCOMPLETE
- at q1: outcome_notes: Travel date required to determine eligibility.
- at q1: summary_notes: User inquires about transportation from Stockton, CA to San Francisco, CA for a maternal-fetal medicine appointment, is on one income.
- at q1: service_region_rationale: Both Stockton, CA and San Francisco, CA are within AFW's service region.
- at q1: within_distance_limit_rationale: The distance between Stockton and San Francisco is approximately 75 miles, well within the 900 mile limit.
- at q1: minimum_notice_rationale: Travel date not yet provided, so minimum notice cannot be determined.
- at q1: requires_small_plane_rationale: This is an in-state transport between two cities within a 900 mile range.
- at q1: requires_commercial_rationale: Route does not warrant commercial airline; small plane is preferred for this distance.
- at q1: summary_compelling_or_financial_need_notes: User cites being on one income, indicating financial need.
- at q1: summary_sentiment_analysis: User appears straightforward and focused on discussing transportation need.

