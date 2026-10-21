# Transcript 04 · The CISO, blocker and admin

> Day 6 discovery pack · Interview 4 of 10 · Persona: admin (security and identity) · Where: her office, Hyderabad HQ; the Kaagaz security lead on a call · When: week 2, Tuesday, 09:00 · Length: 60 minutes · Recording: none · Synthetic conversation for the course.

**In the room:** the CISO (CS); the FDE (F); the Kaagaz security lead (K), remote.

## Conversation

**F:** Last week you asked three questions and I did not have the answers. Today I have the first draft of the questionnaire, and I want to ask you how access works here, because I would rather design for your rules than discover them in month three.

**CS:** Ask.

**F:** When an analyst opens a loan file in the core system, what decides whether she is allowed to?

**CS:** Active Directory. Every user is in a branch group or a regional group, plus a role group. Credit-ops Hyderabad, credit-ops Vijayawada, branch 0417, and so on. The core reads the groups at login. A branch user sees that branch's applications. A regional analyst sees the region. Nobody sees everything except four people in IT and the compliance desk.

**F:** Where do the groups come from?

**CS:** HR. The HR system is the source. There is a nightly sync; HR says "this person is now at Kukatpally", AD moves them. Transfers lag a day. If somebody needs cross-region access we add them by hand, and I do not like it, because by-hand means forgotten.

**F:** Is there a group that means "all branches"?

**CS:** No, and there will not be one for a vendor.

**F:** Then anything we build that retrieves a loan file has to filter by the caller's groups at the moment of the query, not at the time we indexed the file.

**CS:** At the moment of the query. A person who moved branches yesterday should not see the old branch today. And I want to be able to answer "who viewed this file" for any file, for seven years. That is an RBI expectation and it is mine.

**F:** Understood. SSO: can our application authenticate users against your AD?

**CS:** Not as a vendor on the internet, no. On-prem we have AD; the Entra sync is planned for next financial year, not this one. If your application runs in our AWS account in Mumbai, inside our VPC, it can talk to a read-only domain controller after my review. Service accounts go through me personally.

**F:** How long is the review?

**CS:** Eight weeks if your answers are complete the first time. Longer if I have to ask twice.

**F:** The COO has asked for it to start this week. Here is what you need from us: where the PDF goes, what we retain, whether any model trains on your data, which subprocessors touch it, and in which country. The short answers: the PDF never leaves your AWS Mumbai account; we retain nothing on our side; no model is trained on your data and that is in the contract; the model endpoint is in Mumbai.

**CS:** Write it down with the architecture diagram and I will believe the diagram, not the sentences. And the laptop you are using today. Is customer data on it?

**F:** No. Shadowing notes only, with file numbers and no customer names, and I would like you to tell me where those notes should live.

**CS:** On our SharePoint, in a folder I give you. Not on your laptop, not on your company's drive. The same for anything you record. Do not record the analysts without telling HR.

**K:** One question from our side. For the first prototype, before the review completes, where may it run?

**CS:** On a machine in this building, on masked files that the compliance head has approved, with no internet. If that is too slow for you, the review is the answer.

**F:** It is enough. Last question: what would make you say no in week ten?

**CS:** Finding something in week ten I was not told in week two.

## Read-back

Confirmed: group-based visibility, nightly HR sync, no all-branches group, filtering at query time, seven-year view log, no vendor SSO this year, prototype on-prem on masked files, notes on Godavari SharePoint.

## Coded notes

| Code | Verbatim evidence | Kind |
|---|---|---|
| ACCESS_VIA_AD_GROUPS | "Every user is in a branch group or a regional group, plus a role group. The core reads the groups at login." | architecture |
| BRANCH_ISOLATION | "A branch user sees that branch's applications. Nobody sees everything except four people in IT and the compliance desk." | architecture |
| FRESHNESS_NEXT_DAY | "There is a nightly sync. Transfers lag a day." | architecture |
| VIEW_LOG_REQUIRED | "I want to be able to answer 'who viewed this file' for any file, for seven years." | architecture |
| SSO_NOT_AVAILABLE | "Not as a vendor on the internet, no. The Entra sync is planned for next financial year." | constraint |
| NO_PII_OUTSIDE_INDIA | "The PDF never leaves your AWS Mumbai account." (her condition, restated and accepted) | constraint |
| NO_TRAINING_ON_DATA | "No model is trained on your data and that is in the contract." (her question from Day 0, answered) | constraint |
| SECURITY_REVIEW_LONG | "Eight weeks if your answers are complete the first time." | constraint |
| PROTOTYPE_ON_PREM_MASKED | "On a machine in this building, on masked files that the compliance head has approved, with no internet." | constraint |
| NOTES_STAY_ON_SITE | "On our SharePoint, in a folder I give you. Do not record the analysts without telling HR." | constraint |
