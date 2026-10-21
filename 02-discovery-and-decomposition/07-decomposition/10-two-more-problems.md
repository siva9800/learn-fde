# 10 · Two More Problems: Does the Method Transfer?

> Day 7 · Section 10 of 16 · [Chapter overview](README.md) · Previous: [09 · The interview round](09-the-interview-round.md) · Next: [11 · Production concerns](11-production-concerns.md)

---

A method you have only run on one problem is a memory, not a skill. This section runs the five steps on
two problems that look nothing like a loan file: a published interview case about a city's emergency
response, and an Indian logistics case designed for this chapter. Each is written the way you would say
it in the 25-minute protocol, with the reasoning between steps visible, and each ends with what
transferred from Godavari and what did not.

## 10.1 Problem A: a city wants to cut emergency response times

**The prompt (as the Harvard FAS 2026 guide gives it, lightly paraphrased):** a city wants to reduce
911 emergency response times. You have call data, traffic data and ambulance GPS data. You have 60
minutes. Go.

(The Palantir-focused guide uses a near-identical case, "halve emergency dispatch times", with dispatch
logs, vehicle GPS and radio data, and Day 44's drill 1 is the same problem under the clock. The worked
answer here is this chapter's, in the five-step shape.)

### Step 1: clarify

"Response time from which event to which? Call received to unit arrival is the usual definition, but
the city may mean call to dispatch. I will assume call to arrival. Is the target the median or the
tail: a city that is embarrassed by a few 25-minute responses needs different tools from one whose
median is slow. I will assume the median, and I will ask, because the tail is where lives are lost.
Where does the time go today: call handling, the dispatch decision, or driving? My guess is dispatch
and driving, and that guess decides the lever. The trade-off: faster average response against coverage
of outer areas (pre-positioning units near dense areas makes the suburbs slower) and against
dispatcher autonomy. The constraint that cannot move: a public-safety standard for maximum response
time in every zone, and the rule that a human dispatcher makes the dispatch decision. Who sets the
acceptable risk: the EMS chief under that standard, not the mayor who set the goal."

### Step 2: stakeholders and metrics

| Stakeholder | Role | Metric they would accept |
|---|---|---|
| the mayor's office | sponsor | median call-to-arrival, citywide |
| dispatchers | operators | time per dispatch decision; how often they override the tool |
| ambulance crews | operators | wasted drives (dispatched then cancelled); shift fatigue |
| the EMS chief | blocker and the one who sets the risk | 90th percentile response per zone, never worse than today |
| the dispatcher union | blocker | no decision taken away from a dispatcher; no performance scoring of individuals from the tool |
| hospitals | downstream | arrival-to-handover time (a faster ambulance that queues at the door helped nobody) |
| the public-safety regulator | ghost | an audit trail for every dispatch decision |
| the traffic department | upstream data owner | their feed used, not duplicated |

The conflict to carry: the mayor's median improves if units are pulled toward dense areas; the chief's
per-zone 90th percentile forbids it. The skeleton obeys the chief.

### Step 3: map the inputs

| Input | Shape | Owner | Freshness | Access | What is missing | Architecture risk |
|---|---|---|---|---|---|---|
| call records (CAD logs) | one row per call: timestamps for received, dispatched, en route, arrived; priority code; location | the dispatch centre | real time from the dispatch system | an export today; a feed needs the vendor | timestamps entered by hand are unreliable; "arrived" is often pressed late | the baseline needs cleaning before it is a baseline |
| ambulance GPS | a position every 5 to 30 seconds per unit | the fleet contractor | near real time, with gaps in tunnels and garages | a vendor API with a contract clause | unit status (available, busy, out of service) is in the radio system, not the GPS | the join between GPS and status is the hard part, and it will fail |
| traffic data | speeds per road segment per minute | the traffic department | real time, but a different map base from the CAD system | an internal API | no history of incidents (closures, events) | ETAs are only as good as the join to the road network |
| unit status (radio) | a status code per unit, spoken and keyed | dispatch | real time, but keyed late | the radio system's log | often minutes behind reality | the "live map" is wrong whenever status lags |
| hospital capacity | diversion status per hospital | hospitals | hours | a phone call today | not a data source at all | out of scope for the first slice, named as a gap |

Data that does not exist: a clean, agreed definition of "response time" per call with trustworthy
timestamps; this is the city's version of Godavari's ground truth, and the first workstream.

### Step 4: workstreams, sequenced

| Rank | Workstream | Value | Risk | Why here |
|---|---|---|---|---|
| 1 | the data join: GPS plus status plus CAD on one timeline, one map base | 3 | 5 | every later piece depends on it, and it will fail in ways nobody expects |
| 2 | the baseline: clean response times per zone, agreed with the chief | 3 | 4 | without it no claim can be tested, and the per-zone constraint cannot be checked |
| 3 | visibility: a live unit-status map for dispatchers | 4 | 3 | the Palantir guide's point: visibility delivers value before any prediction, and it is how dispatchers learn to trust the data |
| 4 | dispatcher workflow and adoption: how a recommendation appears, how an override is recorded | 3 | 4 | the union's fear and the regulator's audit trail live here |
| 5 | recommendation: nearest-available-by-ETA using traffic, with the dispatcher deciding | 5 | 3 | the value, built on the join and the map |
| 6 | pre-positioning (where idle units should wait), per zone, under the chief's constraint | 4 | 3 | the second lever; only after the first is trusted |

Not now: predicting where calls will occur (no baseline, and it is the thing everyone jumps to); any
tool that scores individual dispatchers.

### Step 5: the walking skeleton

"One district, daytime shifts, one unit type. The live map shows every unit's position and status on
one timeline; when a call comes in, the tool shows the dispatcher the three nearest available units
by traffic-aware ETA; the dispatcher chooses, with one click to override and a reason; the choice and
the actual arrival time are logged against the baseline. Four weeks. It proves the join works, the
status lag is tolerable or not, dispatchers will look at the map, and response time can be measured
per call. Expected failures: status lag makes the map wrong (then status becomes a workstream: a
one-button update in the cab); dispatchers ignore the recommendation (then the recommendation is
hidden and only the map ships for a month); the traffic ETA is worse than the dispatcher's instinct in
the district (then the recommendation uses distance only until the ETA model is validated)."

### What transferred, and what did not

| From Godavari | Transferred? |
|---|---|
| the trade-off is set by a blocker, not the sponsor | yes: the EMS chief, not the mayor |
| the ground truth does not exist and must be created | yes: clean response times per call |
| the riskiest workstream is at a joint, not in a component | yes: the GPS-status-CAD join |
| a deterministic layer the model cannot override | yes: the per-zone standard and the human dispatcher |
| the skeleton is one site, one path, with a human deciding | yes: one district, daytime, one unit type |
| the value workstream is extraction | no: here the first value is visibility, not prediction; the lever is the dispatch decision, not re-keying |
| adoption risk is "analysts keep the spreadsheet" | changed shape: dispatchers ignore the recommendation, and the union can stop the project |

## 10.2 Problem B: a trucking firm wants paid in 15 days, not 45

**The prompt (designed for this chapter; everything is invented):** Rayalaseema Roadways, Kurnool,
runs 800 trucks carrying cement, granite and FMCG goods across Andhra Pradesh, Telangana and Karnataka.
The managing director says: "Our customers pay us 45 days after delivery. The contract says 15. Fix it."
You have the trip records in Tally and a transport management system, proof-of-delivery documents
(signed, stamped delivery challans, photographed by drivers on WhatsApp), e-way bills from the GST
portal, and the accounts team of twelve in Kurnool. Go.

### Step 1: clarify

"Forty-five days measured from delivery to money received? I will assume so, and I will ask whether
the contract's 15 days starts at delivery or at invoice received, because if it is invoice received,
the problem may be that invoices go out late. Where do the 45 days go: is it the customer paying slowly,
or is it us invoicing slowly, or invoices being rejected and resent? My guess, for a trucking firm with
WhatsApp proof of delivery, is that invoices wait for the proof of delivery and then get rejected for
mismatches, and I will come back to that because it decides whether the lever is on our side or the
customer's. The trade-off: speed of invoicing against invoice rejections (an invoice sent fast with a
wrong challan number comes back and costs more days than it saved), and against the accounts team's
time. The constraint that cannot move: GST rules on invoicing and e-way bills, and the customers' own
accounts-payable processes, which we do not control. Who sets the acceptable rejection rate: the
accounts head, against each customer's AP rules."

### Step 2: stakeholders and metrics

| Stakeholder | Role | Metric they would accept |
|---|---|---|
| managing director | sponsor | days sales outstanding (delivery to cash), by customer |
| accounts team (12 people) | operators | invoices raised per person per day; rejections per hundred invoices |
| drivers | upstream operators | proof-of-delivery photos accepted first time; no extra steps at the gate |
| the three largest customers' AP teams | downstream, outside | invoices that match their PO and challan on first receipt |
| the GST consultant | blocker | zero e-way bill or e-invoice mismatches |
| the bank (working-capital line) | ghost | receivables ageing, which sets the interest cost of the 45 days |
| the TMS vendor | system owner | no changes to their data model; an export, not a write |

The conflict: the MD wants invoices out the day of delivery; the accounts head knows a fast wrong
invoice costs 20 days. The skeleton obeys the accounts head: invoice fast only when the three documents
match.

### Step 3: map the inputs

| Input | Shape | Owner | Freshness | Access | What is missing | Architecture risk |
|---|---|---|---|---|---|---|
| trip records (TMS) | one row per trip: truck, driver, route, customer, PO reference, planned quantity | operations | same day | an export; the vendor's API is extra cost | PO reference often typed wrong | the join trip-to-PO is unreliable |
| delivery challans (proof of delivery) | a photo of a signed, stamped paper, from a driver's phone, on WhatsApp | drivers, then the accounts clerk who saves them | same day to a week later | WhatsApp, not a system | missing stamps, unreadable quantities, the wrong trip's challan | an unofficial channel is the system of record; the skeleton has to give drivers an official one that is just as easy |
| e-way bills | structured JSON per consignment from the GST portal | the GST consultant | at dispatch | the portal, with credentials the consultant holds | quantity on the e-way bill versus quantity delivered (shortages) | the three-way match (trip, challan, e-way bill) is the whole product |
| invoices and receipts (Tally) | one entry per invoice; receipt date when money arrives | accounts | daily | Tally export | no record of why an invoice was rejected | no baseline for rejection reasons; must be sampled |
| customer AP rules | a PDF or an email per customer: what an invoice must carry | each customer | changes without notice | nobody has them in one place | undocumented for the smaller customers | the completeness rules per customer are deterministic and must be collected |

Data that does not exist: rejection reasons per invoice for the last three months (the accounts team
samples 200 by hand); the customers' AP rules in one checklist (the accounts head collects them from
the three largest customers first).

### Step 4: workstreams, sequenced

| Rank | Workstream | Value | Risk | Why here |
|---|---|---|---|---|
| 1 | the baseline and rejection reasons: 200 invoices, where the 45 days go | 3 | 5 | it decides whether the lever is on our side; if customers simply pay late, the project is a collections project, not a documents project |
| 2 | the three-way match: trip, challan, e-way bill, as deterministic rules | 5 | 4 | the core of the value; the join is where it will fail |
| 3 | proof-of-delivery capture: an official channel for drivers that is as easy as WhatsApp | 4 | 4 | adoption: drivers will not use anything slower than a photo |
| 4 | challan reading: quantity, date, stamp present, signature present, from a phone photo | 4 | 4 | the extraction piece; judged against a labelled set the accounts team builds |
| 5 | customer AP rules as a checklist per customer | 3 | 2 | low risk, high value, thin version in the skeleton for the largest customer |
| 6 | invoicing and Tally integration: an invoice raised the day all three match | 4 | 3 | the output; an export-and-import first, a write later |

Not now: predicting which customers will pay late; chasing customers (a collections workflow, different
operators); any change to the TMS data model.

### Step 5: the walking skeleton

"One customer (the largest cement buyer), one route, one month. A driver uploads the challan photo
through a one-screen form instead of WhatsApp; the tool reads quantity, date, and whether the stamp
and signature are present; it matches the trip's PO, the challan and the e-way bill; if all three
match it prepares the invoice for the accounts clerk to approve in Tally; if not, it tells the clerk
and the driver exactly what is missing the same day. Every invoice is timed from delivery to raised,
and from raised to paid. Three weeks. It proves drivers will use the form, the three-way match catches
the rejections, and days-to-invoice can be measured. Expected failures: drivers keep using WhatsApp
(then the form becomes a WhatsApp bot, which changes the security conversation); the e-way bill
quantities never match the challan because of accepted shortages (then shortage tolerance is a rule the
accounts head signs); the customer rejects for reasons that are not on any checklist (then the AP-rules
workstream moves first)."

### What transferred, and what did not

| From Godavari | Transferred? |
|---|---|
| the first workstream is finding out where the time goes | yes, and here it could change the whole project (collections, not documents) |
| an unofficial channel (WhatsApp) is the real system of record | yes, and here it cannot be banned; the skeleton has to replace it with something as easy |
| a deterministic layer the model cannot override | yes: the three-way match and the customer checklists |
| the skeleton is one customer, one route, with a human approving | yes |
| the regulator's rules are fixed inputs | yes: GST, e-way bills |
| the blocker who sets the trade-off is inside the company | partly: the accounts head is, but the customers' AP teams are outside and cannot be interviewed as operators |
| the sponsor's metric and the blocker's constraint conflict | yes, same shape: fast versus correct |

## 10.3 What the three runs have in common

Put Godavari, the city and the trucking firm side by side and the method's shape is the same every time:

| Step | The pattern that repeats |
|---|---|
| 1 | the sponsor's number hides a unit and a trade-off; the person who sets the acceptable loss is a blocker |
| 2 | there is always an upstream producer (branches, the traffic department, drivers), a system owner, and a ghost (the auditor, the regulator, the bank) |
| 3 | there is always an unofficial channel, a join that will fail, and ground truth that does not exist |
| 4 | the riskiest workstream is a joint or a baseline, never the model; adoption is a workstream |
| 5 | one site, one path, a human deciding, measured; the failures expected are the ones the inputs table predicted |

That is what "the method transfers" means. Day 42's capstone (a hospital network's discharge summaries
and insurance pre-authorisation) and Day 44's ten drills are the same shape again. By the third run the
questions come without thinking, which is the point of drilling it.

## 10.4 Key takeaways

- On a city's emergency response the first value is visibility, not prediction, and the riskiest
  workstream is the GPS-status-CAD join.
- On a trucking firm's receivables the first workstream decides whether the project is about documents
  at all, and the unofficial channel must be replaced by something as easy, not banned.
- Across all three problems the shape repeats: a hidden trade-off set by a blocker, missing ground
  truth, a failing join, adoption as a workstream, a thin slice with a human deciding.
