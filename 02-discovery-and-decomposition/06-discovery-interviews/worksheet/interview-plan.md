# Godavari discovery interview plan · weeks 1 and 2

> Day 6 artifact. Drawn from the Day 5 stakeholder map before the first interview; updated as interviews happened. The rule: 8 to 10 end users across roles and both cities, plus the admins and the sponsor, before any production code. Shadowing precedes the operator interviews so that the questions come from what was seen. Synthetic.

## Roster

| # | Who | Persona | City | Why them | When | Shadowed first? | Done |
|---|---|---|---|---|---|---|---|
| 1 | Lakshmi, analyst, 11 years | operator, eval owner | Vijayawada | the person Day 0 sat beside; owns the tracker in practice | W1 Wed | yes, full morning | yes |
| 2 | Srinivas, team lead | operator lead | Hyderabad | assigns the queue; the manual AD exception | W1 Thu | floor walk W1 Mon | yes |
| 3 | The COO | sponsor | Hyderabad | the number; what must never be automated | W2 Mon | n/a | yes |
| 4 | The CISO | admin (security, identity) | Hyderabad | access, SSO, residency, where notes live | W2 Tue | n/a | yes |
| 5 | The compliance head | admin (rules) | Hyderabad | the fixed rules, the judgement, the auditor's voice | W2 Mon | n/a | yes |
| 6 | The core-system owner | admin (system owner) | Hyderabad DC | the batch, the API, the sandbox, three failed vendors | W1 Thu | n/a | yes |
| 7 | Kukatpally branch manager | upstream producer | Hyderabad | the COO's "best branch that complains most"; the pilot branch | W2 Wed | watched the 17:00 scan | yes |
| 8 | Guntur branch manager | upstream producer, far branch | Guntur (phone) | most phone photos in the region per the tracker | W2 Wed | no | yes |
| 9 | Senior analyst, Hyderabad | operator, sceptic, eval owner | Hyderabad | caught the 2019 OCR failure; her failure model | W1 Tue | yes, afternoon | yes |
| 10 | Bhavani, junior analyst | operator, junior | Vijayawada | the newest person: how the job is really learned | W2 Thu | yes, one full file | yes |

Not interviewed, by design: the RBI auditor (ghost; the compliance head speaks for him); the corporate IT identity team (a 20-minute call in week 2 confirmed the HR sync and the ticket process; no transcript); the Vijayawada team lead (sat in on interview 1 and the Friday review; the champion, met daily rather than interviewed).

**Against Day 2's calendar.** Day 2's two-week calendar was drafted the Friday before the engagement started. Five sessions here did not fit it and were added around it: the senior analyst (week 1 Tuesday, after the shadowing, in place of the first extraction run), the COO (week 2 Monday, the last hour), the two branch managers (week 2 Wednesday, around the labelling call), and Bhavani (week 2 Thursday, a second Vijayawada visit that pushed the integration spike to the afternoon). Two days ran past nine hours. That is normal in discovery weeks; Day 2's section 07 covers what it costs.

## Coverage check

| Dimension | Covered by |
|---|---|
| Both cities | 1, 10 (Vijayawada); 2, 9 (Hyderabad); 8 (Guntur, far branch) |
| Senior and junior | 1, 9 (senior); 10 (junior) |
| Operators and upstream producers | 1, 2, 9, 10; 7, 8 |
| Every blocker from the map | 4, 5, 6 |
| The sponsor | 3 |
| The sceptic | 9 |
| The eval owners | 1, 9 (fields); 5 (completeness) |

## Sequencing rules used

1. Shadow before interviewing an operator; interview the same day while the observations are fresh.
2. Operators before the sponsor, so that the sponsor's version can be tested against the floor's.
3. Blockers in week one or two, not week ten (Day 5).
4. The system owner before reading the WSDL in anger; the WSDL before the second meeting.
5. Synthesise after every three or four interviews, not once at the end.
6. Read the notes back at the end of every interview; file the notes on Godavari's SharePoint the same day (the CISO's rule).
