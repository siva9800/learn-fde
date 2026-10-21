# 05 · Two Weeks at Godavari: The Calendar, Hour by Hour

> Day 2 · Section 5 of 12 · [Chapter overview](README.md) · Previous: [04 · The 60/30/10 week](04-the-60-30-10-week.md) · Next: [06 · Titles, neighbours and three employers](06-titles-neighbours-and-three-employers.md)

---

## 5.1 The brief, and the rule

It is the Friday before the engagement starts. The Kaagaz engagement lead asks for the first two weeks
as a calendar, so that Godavari's COO knows when you need whom, and so that the Kaagaz product team
knows when to expect something back. You draft it as hour blocks, each tagged with its bucket, in
[`worksheet/godavari-weeks-1-2-calendar.md`](worksheet/godavari-weeks-1-2-calendar.md). The rule you
set yourself: **do not plan for a split. Plan the work, then count.** If the fortnight lands near
60/30/10 without trying, the split is a description of the job; if it does not, the calendar or the
split is wrong, and you want to know which.

Week 1 is the week Day 0 told as a story, now with hours. Week 2 adds the integration spike and the
first write-up for product, which the Part 1 plan calls for. Both weeks are invented; every person at
Godavari is invented; the hours are what a careful FDE would plan, not what any real engagement did.

## 5.2 Week 1 · discovery, on site

| Day | Where | The blocks | Buckets |
|---|---|---|---|
| **Monday** | Hyderabad HQ | 09:00 the COO's kickoff, "nine days to three", and the question you write down · 10:00 walk the credit-ops floor with Srinivas, the Hyderabad team lead · 13:00 three hours alone with their SOP, the sales notes and the demo deck, listing every claim the deck makes · 16:00 access requests with the helpdesk: VPN, document store, core-system test login · 17:00 Kaagaz daily sync, open the engagement log | C 6, D 1, I 0.5 |
| **Tuesday** | Hyderabad HQ | 09:00 the CISO: where does the PDF go, does your model train on our data, which country is the server in; no, no, not yet · 10:30 write her questions down verbatim and start the questionnaire draft · 13:00 shadow two analysts on the queue: what they open first, what they wait for, what they type twice · 15:00 run the extraction demo locally on real sample slips and statements; it reads 2 of 14 types well · 17:00 log | C 5, D 2, I 0.5 |
| **Wednesday** | Vijayawada | 09:30 a full morning beside Lakshmi: the 2009 screens at forty seconds a load, and the Excel tracker nobody mentioned · 14:00 the tracker column by column with Lakshmi and the Vijayawada team lead · 16:00 shadowing notes on the train home | C 7 |
| **Thursday** | Hyderabad HQ | 09:00 count with Srinivas and two analysts: documents per file, which document the queue waits on most · 11:00 the core-system owner: the 6 pm credit-check batch, the sandbox and its refresh · 13:00 read the WSDL, list the SOAP operations · 15:00 the COO in the corridor, "so when will we be at three days?"; you ask for twenty minutes on Friday · 15:15 draft the readout | C 5, D 2 |
| **Friday** | Hyderabad HQ | 09:00 page one of the discovery document, which does not mention the model · 13:00 the twenty-minute readout · 14:00 Kaagaz product: the tracker as the real state, the 2-of-14 finding · 15:30 plan week 2 · 16:00 re-read the shadowing notes, list the questions for week 2 | C 4.5, I 2 |

**Week 1: 35.5 hours. Customer-facing 27.5 (77 percent), deployment code 5 (14 percent), internal 3 (8
percent).** That is not 60/30/10, and it should not be. Week one of an engagement is discovery, and
discovery is bucket 3. The deployment hours that exist (the access requests, the demo run, the WSDL) are
there to make week two possible.

## 5.3 Week 2 · the spike, and the first write-up

| Day | Where | The blocks | Buckets |
|---|---|---|---|
| **Monday** | Hyderabad HQ | 09:00 Kaagaz weekly planning · 10:00 second shadowing pass, only send-back cases: why does a file come back? · 13:00 the compliance head: which KYC rules are fixed, which are judgement, who signs a change · 15:00 start the SOAP sandbox client, WSDL to a typed stub | I 1, C 4, D 2 |
| **Tuesday** | Hyderabad HQ | 09:00 three hours with the Kaagaz security lead filling the questionnaire draft for the CISO: residency, retention, training-use policy, subprocessors · 13:00 four hours running extraction on 20 sample files from one branch, measured field by field on bank statements | C 3, D 4 |
| **Wednesday** | desk, plus a call | 09:00 label 30 files with Lakshmi on a call: the first seeds of the golden set (Day 14 builds it properly) · 13:00 run extraction on the 30 labelled files, sort the failures by type · 16:00 note the failure types for product: Telugu address proofs, stamped bank statements | C 3, D 3, I 1 |
| **Thursday** | desk | 09:00 the integration spike: CreateApplication against the sandbox; the timeout; the duplicate record on retry · 14:00 show the duplicate to the core-system owner, ask about idempotency, agree the sandbox refresh date · 15:00 make the retry safe with a client-side key, log every call | D 6, C 1 |
| **Friday** | Hyderabad HQ | 09:00 write the week's status for the COO: what was found, what was measured, what is next · 11:00 readout · 13:00 the pattern memo for Kaagaz product: tracker-as-state, the idempotency key, the 2-of-14 gap · 15:00 plan week 3 · 16:00 reply in writing to the CISO's follow-up questions | C 4, I 3 |

**Week 2: 35 hours. Customer-facing 15 (43 percent), deployment code 15 (43 percent), internal 5 (14
percent).** The spike and the measured extraction run push deployment code to the same weight as the
customer. The internal slice grows because there is now something worth sending back: three patterns
the product team can act on.

## 5.4 The count

`code/week_hours.py` reads the calendar, checks that every block's hours match its clock times and that
no day exceeds nine hours, and sums by bucket:

```text
== godavari-weeks-1-2-calendar.md: 40 blocks across 2 week(s) ==
Week 1: 35.5 hours
  customer-facing  27.50 h   77.5%   (reference 60%)
  deployment code   5.00 h   14.1%   (reference 30%)
  internal          3.00 h    8.5%   (reference 10%)
Week 2: 35 hours
  customer-facing  15.00 h   42.9%   (reference 60%)
  deployment code  15.00 h   42.9%   (reference 30%)
  internal          5.00 h   14.3%   (reference 10%)
Both weeks: 70.5 hours
  customer-facing  42.50 h   60.3%   (reference 60%)
  deployment code  20.00 h   28.4%   (reference 30%)
  internal          8.00 h   11.3%   (reference 10%)

lands at about 60/28/11 against the 60/30/10 that postings describe
customer-facing hours were spent with 12 different people or groups:
  - Kaagaz security lead, for the CISO
  - Lakshmi and the Vijayawada team lead
  - Lakshmi, Vijayawada
  - Lakshmi, on a call
  - Srinivas and two analysts
  - Srinivas, Hyderabad credit-ops team lead
  - the CISO
  - the COO
  - the COO, in the corridor
  - the compliance head
  - the core-system owner
  - two Hyderabad analysts
```

**The fortnight lands at 60/28/11.** Nobody planned a split; the work was planned and then counted. Two
weeks that individually look nothing like 60/30/10 (77/14/8 and 43/43/14) average to it, which is the
honest shape of the figure: a description of an engagement, not of any one week.

## 5.5 What to notice in the calendar

- **Twelve different people in two weeks.** The sponsor, two team leads, four analysts, Lakshmi, the
  CISO, the compliance head, the core-system owner, and Kaagaz's own security lead on the customer's
  behalf. Day 5's stakeholder map is most of this list; bucket 3 is where it gets drawn.
- **Every deployment block has a customer-facing block before it.** The WSDL reading follows the
  core-system owner meeting; the extraction run follows the shadowing; the spike follows the compliance
  head and the WSDL. Section 04.3's claim, visible in the table.
- **The internal slice is small and specific.** Three patterns and a plan, not "sync with product". If
  the internal hours are not producing something the product team can act on, they are overhead.
- **The CISO's no on Tuesday did not stop the fortnight.** With visitor Wi-Fi and no credentials, there
  were still 70 hours of real work, and the questionnaire draft started the clock on the review (Day 23).
  Access is on the critical path; it is not the whole path.
- **Friday is the readout, both weeks.** Day 29 teaches how to write it; the calendar just makes sure the
  hour exists.

## 5.6 Key takeaways

- Plan the work, then count; do not plan for a split.
- Week 1 is 77 percent customer-facing and week 2 is 43 percent; the fortnight is 60/28/11.
- Twelve people in two weeks; every deployment block has a customer-facing block before it; the internal
  slice produces patterns, not meetings.
- The split describes an engagement, not a week. Any single week that matches it exactly is probably
  being planned backwards from the figure.
