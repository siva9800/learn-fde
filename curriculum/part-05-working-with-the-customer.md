# Part 5 · Working With the Customer

> Communication taught as an engineering skill: the weekly readout, bad news, demos that build trust, the governance line you must hold, adoption, and six scripted client-simulation drills, all drawn from the Godavari engagement · Days 29 to 34 · 6 episodes · ~72 min

*Why this Part exists in 2026: customer-facing skills appear in 70 percent or more of FDE
postings and are the fastest-growing requirement, and the client-simulation round is where
otherwise strong engineers fail. An FDE spends roughly 60 percent of the week with the customer.
The code from Parts 3 and 4 is only worth anything if a COO reads the readout, a CTO still trusts
you after a slip, forty analysts choose to use the system, and you can say no to the feature that
would break data governance without losing the room. These chapters are about people and
judgement and should barely date.*

---

### Day 29 · Communication for engineers: status updates, the weekly readout, writing for a COO (~11 min)
- **Status:** new.
- **What you learn:** how to write the weekly readout a sponsor forwards to the CEO, how to run a status call that ends in decisions, and how to pick the one number each audience needs. This chapter owns status communication; every later conversation is a variation on it, and interviewers score it directly.
- **Topics:**
  - The readout structure: outcome metric, this week, next week, risks, asks, decisions needed
  - Writing for the reader's question, not your week: the COO, the CISO and the operators each want something different
  - One number per audience, with its baseline and its date
  - The no-jargon test: replace "chunking" and "p95" with what they cost or save
  - The running decision log the customer can search, and meeting notes within 24 hours
  - Bilingual rooms: Telugu in the branch, English in the boardroom, one language in the written record
- **Real-time example:** your week-4 readout to Godavari's COO. The first draft is 900 words. The second reads: "Pilot turnaround: 9 days to 6.5 on 120 sample files. Blocked on AD group sync; ask: two days from the CISO's team. Next: UAT with ten analysts." She forwards the second to the CEO unchanged.
- **Analogy (Telugu audience):** the cricket scoreboard. The captain needs runs, wickets and overs left, not the bowler's analysis of seam position, however correct it is.
- **Shorts:**
  - "Your readout should survive being forwarded to the CEO without an explanation."
  - "One number, its baseline, its date. That is a status update."
- **Callbacks:** builds on D9 (the metric you chose), D10 (the discovery document), D28 (the readout that reports done). Sets up D30, D31, D34, D45.

### Day 30 · Delivering bad news: the slip, the outage, the result that is worse than the demo (~12 min)
- **Status:** new.
- **What you learn:** how to tell a customer something they do not want to hear, early enough that they can act on it, in a way that leaves trust higher than before. Three cases: a three-week slip with the CTO on the call, a production outage, and a production result worse than the demo.
- **Topics:**
  - No surprises in a steering meeting: bad news travels first in a direct message, then in the room
  - The five-part script: fact and date, cause in one sentence, what it means for them, options with trade-offs, what you will do by when
  - Ownership language: "I missed this" over "the model" or "the vendor"
  - Diagnosing before proposing
  - The worse-than-demo result: explaining distribution shift to a sponsor without the word
  - The trust ledger: what each honest conversation deposits, and what one hidden slip withdraws
- **Real-time example:** the SOAP integration from Day 16 is three weeks late because the 2009 core system's test environment does not match production, and the CTO joins the Friday call. You lead with the new date, the cause, two options (manual entry for three weeks, or wait) and what you will confirm by Monday. Then the Day 27 outage, and the week production accuracy is 82 percent against 94 in the demo.
- **Analogy (Telugu audience):** the family doctor with a bad report. She tells the family early, in plain words, with the next step.
- **Shorts:**
  - "Bad news early is a deposit. Bad news late is a withdrawal, with interest."
  - "Three weeks late, CTO on the call. Here is the first sentence."
- **Callbacks:** builds on D14, D27 (the incident itself), D29. Sets up D31, D34 (drills 1 and 3), D45.

### Day 31 · Demos and workshops that build trust: the Morgan Stanley lesson (8 weeks to build, 4 months to trust) (~12 min)
- **Status:** new.
- **What you learn:** why a working system is not an adopted system, and how demos, pilots and labelling workshops close the gap. Morgan Stanley's advisor assistant was technically ready in roughly six to eight weeks, then took about four more months of pilots, advisor labelling and eval refinement before the reported 98 percent adoption and roughly three times the usage.
- **Topics:**
  - The demo-to-trust gap, and why it is where the customer's experts are recruited
  - Demo discipline: their documents, live, with a failure shown on purpose and handled
  - The labelling workshop: operators score real cases, disagreements join the golden set (Day 14), evals and trust grow together
  - Pilot design: cohort size, duration, what counts as done
  - Champions: the sceptic who becomes the advocate is worth more than the enthusiast
  - Measuring trust: unprompted usage, and the operator who corrects the system instead of ignoring it
- **Real-time example:** the pilot workshop in Vijayawada with ten analysts. Each labels twenty loan files against the system's output; every disagreement becomes an eval case. The senior analyst who said "it will never read handwritten income proofs" watches it flag them for review instead of guessing, and by week three she is the champion.
- **Analogy (Telugu audience):** biryani at a new restaurant. The first order is curiosity, the fiftieth is trust, and the owner who lets you watch the dum opened is the one you bring your family to.
- **Shorts:**
  - "Morgan Stanley: eight weeks to build, four months to trust. Plan for the four months."
  - "The best champion is the analyst who said it would never work."
- **Callbacks:** builds on D14, D18 (reasoning in the interface), D29. Sets up D33, D34 (drill 4), D37.

### Day 32 · Scope, pushback and the governance line: when the customer asks for the thing you must refuse (~12 min)
- **Status:** new.
- **What you learn:** how to say no to a customer and keep the engagement. Four refusals are scripted: a feature that would break data governance, a disagreement with the customer's architecture, a security team refusing production credentials, and a VP asking for 100 percent.
- **Topics:**
  - The governance line: purpose limitation, retention and the residency annex (Day 24) are not tradeable, however senior the asker
  - The no with an alternative: what you can do, by when, and what the original would take
  - Disagreeing with their architecture: say what you would do and why, ask what you are missing, build what they decide, record it
  - No production credentials: synthetic data, their engineer running your commands, break-glass with an audit trail
  - Why retrieval cannot guarantee 100 percent, and what you can guarantee: confidence routing, the review queue, a measured error rate with a trend
  - Scope creep by kindness, the Day 8 scope document, and the one-page decision record
- **Real-time example:** Godavari's sales VP asks to add customer phone numbers and call recordings to the index "so the model knows the customer". You refuse on DPDP purpose limitation and the retention annex, propose a separately consented workflow for a later phase, and the compliance head backs you in the meeting.
- **Analogy (Telugu audience):** village elders. The one who says "no, and here is what we can do" is the one families bring disputes to.
- **Shorts:**
  - "The customer asked for the feature that breaks data governance. No, and here is the alternative."
  - "Retrieval cannot promise 100 percent. Here is what it can promise."
- **Callbacks:** builds on D8, D11 (deterministic versus LLM), D23, D24. Sets up D34 (drills 2, 3, 5), D41, D45.

### Day 33 · Adoption: why curiosity starts use and value sustains it, and the operator who will not switch (~11 min)
- **Status:** new.
- **What you learn:** what makes forty analysts keep using a system after the novelty is gone, how to measure adoption honestly, and what to do about the operator who will not switch. Atlassian's finding anchors it: curiosity drives initial adoption, value sustains it, and the most-used AI sits inside tools people already use.
- **Topics:**
  - Curiosity versus value: the week-2 peak, the week-6 trough, and what survivors have in common
  - Inside the tools they already use: the review queue in the loan-origination screen, not a new tab
  - Honest adoption metrics: weekly active operators, documents through the system versus around it
  - The operator who will not switch: fear of blame, muscle memory, a slower first week, an incentive that did not change
  - Shadowing again (Day 6) and feedback capture (Day 19): find the real reason, act on corrections within a week
  - When not to force it: the workflow where manual is genuinely better
- **Real-time example:** six weeks after go-live, 31 of 40 analysts use the system daily; nine in Vijayawada still key in by hand. Shadowing finds the reason: the branch manager counts keystrokes for appraisals, and the system saved time without changing their number. The fix is a conversation with the COO, not a feature.
- **Analogy (Telugu audience):** UPI. Nobody adopted it from a training session. It sat inside the phone people already held, the chai stall took it, and value did the rest.
- **Shorts:**
  - "Curiosity starts adoption. Value sustains it. Week six is where you find out which you have."
  - "Nine analysts will not switch. The reason is on the appraisal sheet, not in the code."
- **Callbacks:** builds on D6, D19, D28, D31. Sets up D34 (drill 4), D37, D38.

### Day 34 · Client simulation drills: six scripted scenarios with model responses (~14 min)
- **Status:** new.
- **What you learn:** six scripted conversations from the Godavari engagement, each with the customer's opening line, a weak response, a model response annotated against the interviewers' rubric, and the written follow-up. The rubric scores ownership language over deflection, diagnostic questions before proposals, acknowledging what the customer is right about, options with trade-offs, and never overpromising.
- **Topics:**
  - Drill 1: the frustrated CTO on the three-week slip (Day 30)
  - Drill 2: the security team refusing production credentials (Day 32)
  - Drill 3: the VP who wants 100 percent accuracy before go-live (Day 32)
  - Drill 4: the senior analyst who will not use the system (Days 31, 33)
  - Drill 5: the sponsor adding scope before value is shown (Days 8, 32)
  - Drill 6: the compliance head asking "prove no model trains on our data" with the auditor present (Day 23)
  - The phrases that lose points: "we" instead of "I", jargon, agreeing too fast, promising a date you do not own
  - Practice: record yourself, time the opening, swap roles, keep the follow-up under 150 words
- **Real-time example:** every drill is a scene with Godavari's cast: the CTO on Friday's call, the CISO's team, the sales VP, the Vijayawada analyst, the COO adding e-KYC to the scope, the compliance head with the RBI auditor. Model responses reuse Day 29's structure and Day 30's script.
- **Analogy (Telugu audience):** exam prep. Nobody clears EAMCET on theory alone; the mock test under time pressure is where the reflex forms.
- **Shorts:**
  - "Client simulation round: six scenarios, one rubric, and the phrase that loses the most points."
  - "Say 'I', not 'we'. Interviewers are listening for ownership."
- **Callbacks:** builds on D23, D29 to D33. Sets up D43 (the interview loop), D45, D46.

---

## Research sources

- Atlassian, Forward Deployed Engineering Playbook: "curiosity drives initial adoption, value sustains it", and the finding that the most-used AI sits inside tools people already use. https://www.atlassian.com/blog/guides-research/forward-deployed-engineering-playbook and https://www.atlassian.com/enterprise/success/fde
- OpenAI, Morgan Stanley customer story (98 percent adoption in wealth management; document access from 20 to 80 percent): https://openai.com/index/morgan-stanley/ and the AI in the Enterprise guide https://cdn.openai.com/business-guides-and-resources/ai-in-the-enterprise.pdf
- ZenML LLMOps database, OpenAI forward deployed engineering (the Morgan Stanley timeline of weeks to build and months of pilots, advisor labelling and eval refinement; the usage multiple): https://www.zenml.io/llmops-database/forward-deployed-engineering-bringing-enterprise-llm-applications-to-production and https://www.zenml.io/llmops-database/forward-deployed-engineering-for-enterprise-llm-adoption
- Harvard FAS Career Services, the FDE interview, 2026 guide (the client-simulation round and what it scores): https://careerservices.fas.harvard.edu/blog/2026/08/01/forward-deployed-engineer-interview-the-definitive-2026-guide-fde/
- The FDE playbook: a practitioner's field manual (status communication, pushback, the governance line): https://conikeec.substack.com/p/the-forward-deployed-engineer-playbook
- How FDEs run customer discovery in 2026 (shadowing and the questions that reveal the real reason): https://getperspective.ai/blog/how-forward-deployed-engineers-run-customer-discovery-2026
- FDE first 90 days (readouts, pilots, champions): https://cloudsoftsol.com/blog/fde-first-90-days
- 2026 FDE hiring trends: what 1,000 job posts reveal (customer-facing skills in 70 percent or more of postings): https://getperspective.ai/blog/2026-fde-hiring-trends-what-1000-job-posts-reveal

## Notes for writers

- Day 29 owns status communication. Days 30 and 31 extend it and must reuse its readout structure rather than inventing a new one.
- Day 27 owns the incident process; Day 30 owns only the conversation about the outage.
- Day 32 handles the refusal of a questionnaire item or a governance-breaking feature; the questionnaire itself is Day 23's.
- Morgan Stanley figures: say "roughly six to eight weeks" and "about four more months", and quote 98 percent adoption and roughly three times usage as reported by the company and OpenAI, with the date. Do not add advisor headcounts or model names from secondary write-ups.
- All Godavari numbers (120 sample files, 6.5 days, 82 versus 94 percent, 31 of 40 analysts) are synthetic and belong to the invented engagement.
- Day 34's six drills must each be answerable in under three minutes aloud, with the model response printed in full and annotated against the rubric.
