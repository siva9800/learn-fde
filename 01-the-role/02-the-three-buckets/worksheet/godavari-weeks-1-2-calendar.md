# Godavari engagement · weeks 1 and 2 as a calendar

> Day 2 artifact for the engagement folder. Every working block of the first two weeks, with the bucket
> it belongs to. Week 1 is the week Day 0 told as a story; week 2 adds the integration spike and the
> write-up for the Kaagaz product team. Run `python -X utf8 code/week_hours.py worksheet/godavari-weeks-1-2-calendar.md`
> from the chapter folder to count hours per bucket.

**Customer:** Godavari Finance Ltd, Hyderabad · **Vendor:** Kaagaz AI · **FDE:** you · **Dates:** two weeks from the Monday after the deal closed

Buckets: **C** customer-facing (with the customer's people, on their problem, including reading their
documents and writing for them) · **D** deployment code (code, environments and access for this
deployment) · **I** internal (Kaagaz: product team, patterns, planning, the engagement log). Travel and
lunch are not counted.

## Week 1 · discovery, on site

| Day | Start | End | Hours | Bucket | With | What |
|---|---|---|---|---|---|---|
| Mon | 09:00 | 10:00 | 1 | C | the COO | Kickoff in the fourth-floor glass room: "nine days to three"; you write down "nine days doing what?" |
| Mon | 10:00 | 12:00 | 2 | C | Srinivas, Hyderabad credit-ops team lead | Walk the floor; watch the queue; first look at the 14-document checklist |
| Mon | 13:00 | 16:00 | 3 | C | alone, their documents | Read the loan-origination SOP, the sales notes and the demo deck side by side; list every claim the deck makes |
| Mon | 16:00 | 17:00 | 1 | D | Godavari IT helpdesk | Access requests: VPN, document store read access, core-system test login |
| Mon | 17:00 | 17:30 | 0.5 | I | Kaagaz engagement lead | Daily sync; open the engagement log |
| Tue | 09:00 | 10:30 | 1.5 | C | the CISO | "Where does the PDF go?" "Does your model train on our data?" "Which country is the server in?" Answer: no, no, not yet |
| Tue | 10:30 | 12:00 | 1.5 | C | alone | Write up every CISO question verbatim; start the security questionnaire draft (Day 23 finishes it) |
| Tue | 13:00 | 15:00 | 2 | C | two Hyderabad analysts | Shadow the queue: what they open first, what they wait for, what they type twice |
| Tue | 15:00 | 17:00 | 2 | D | alone, Kaagaz platform | Run the extraction demo locally on sample salary slips and bank statements; note it reads 2 of the 14 document types well |
| Tue | 17:00 | 17:30 | 0.5 | I | alone | Engagement log |
| Wed | 09:30 | 13:00 | 3.5 | C | Lakshmi, Vijayawada | Shadow a full morning: the 2009 screens at forty seconds a load, and the Excel tracker nobody mentioned |
| Wed | 14:00 | 16:00 | 2 | C | Lakshmi and the Vijayawada team lead | Go through the tracker column by column: "waiting on bank statement since", "called customer, no answer" |
| Wed | 16:00 | 17:30 | 1.5 | C | alone, on the train | Write the shadowing notes while they are fresh; the nine days live in the spreadsheet |
| Thu | 09:00 | 11:00 | 2 | C | Srinivas and two analysts | Count: documents per file, which document the queue waits on most |
| Thu | 11:00 | 12:00 | 1 | C | the core-system owner | The 6 pm credit-check batch; the sandbox and how often it is refreshed |
| Thu | 13:00 | 15:00 | 2 | D | alone | Read the 2009 system's WSDL; list the SOAP operations and what CreateApplication needs |
| Thu | 15:00 | 15:15 | 0.25 | C | the COO, in the corridor | "So when will we be at three days?" You ask for twenty minutes on Friday |
| Thu | 15:15 | 17:00 | 1.75 | C | alone | Draft the Friday readout: the document the queue waits on, the batch job, the tracker |
| Fri | 09:00 | 12:00 | 3 | C | alone | Page one of the discovery document; it does not mention the model |
| Fri | 13:00 | 13:30 | 0.5 | C | the COO | The twenty-minute readout |
| Fri | 14:00 | 15:30 | 1.5 | I | Kaagaz product team | First patterns: the tracker as the real state; the model reads 2 of 14 types |
| Fri | 15:30 | 16:00 | 0.5 | I | Kaagaz engagement lead | Plan week 2 |
| Fri | 16:00 | 17:00 | 1 | C | alone | Re-read the shadowing notes; list the questions for week 2 |

## Week 2 · the spike, and the first write-up

| Day | Start | End | Hours | Bucket | With | What |
|---|---|---|---|---|---|---|
| Mon | 09:00 | 10:00 | 1 | I | Kaagaz weekly planning | Engagement status to the team; what product needs from you this week |
| Mon | 10:00 | 12:00 | 2 | C | two Hyderabad analysts | Second shadowing pass, only on send-back cases: why does a file come back? |
| Mon | 13:00 | 15:00 | 2 | C | the compliance head | The KYC checklist: which rules are fixed, which are judgement, who signs a change |
| Mon | 15:00 | 17:00 | 2 | D | alone | Start the SOAP sandbox client: WSDL to a typed stub |
| Tue | 09:00 | 12:00 | 3 | C | Kaagaz security lead, for the CISO | Fill the questionnaire draft: residency, retention, training-use policy, subprocessors |
| Tue | 13:00 | 17:00 | 4 | D | alone | Run extraction on 20 sample files from one Hyderabad branch; measure field by field on bank statements |
| Wed | 09:00 | 12:00 | 3 | C | Lakshmi, on a call | Label 30 files together: the first seeds of the golden set (Day 14 builds it properly) |
| Wed | 13:00 | 16:00 | 3 | D | alone | Run extraction on the 30 labelled files; sort the failures by type |
| Wed | 16:00 | 17:00 | 1 | I | Kaagaz product team | Note the failure types for product: Telugu address proofs, stamped bank statements |
| Thu | 09:00 | 13:00 | 4 | D | alone | Integration spike: CreateApplication against the sandbox; the timeout; the duplicate record on retry |
| Thu | 14:00 | 15:00 | 1 | C | the core-system owner | Show the duplicate; ask about idempotency; agree the sandbox refresh date |
| Thu | 15:00 | 17:00 | 2 | D | alone | Make the retry safe with a client-side key; log every call |
| Fri | 09:00 | 11:00 | 2 | C | alone | Write the week's status for the COO: what was found, what was measured, what is next |
| Fri | 11:00 | 12:00 | 1 | C | the COO | Readout |
| Fri | 13:00 | 15:00 | 2 | I | Kaagaz product team | Write up three patterns: tracker-as-state, the idempotency key, the 2-of-14 document gap |
| Fri | 15:00 | 16:00 | 1 | I | Kaagaz engagement lead | Plan week 3 |
| Fri | 16:00 | 17:00 | 1 | C | alone | Reply in writing to the CISO's follow-up questions |
