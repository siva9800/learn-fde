# 11 · Exercises

> Day 5 · Section 11 of 12 · [Chapter overview](README.md) · Previous: [10 · Interview questions](10-interview-questions.md) · Next: [12 · Further reading](12-further-reading.md)

---

Ten exercises in three levels, including two out-loud drills and one "review this AI-written
map". Solutions are folded under each one. The exercises marked **(tested)** use the chapter's
script, run on Python 3.14.3 (October 2026) from the chapter folder, and the outputs shown are
real. Learning mode: do the thinking yourself; use an AI assistant as the persona or the sceptical
reviewer (section 08.6's prompts), not as the author. Try first, then open.

## Level 1: warm-up (no code needed)

**1.1 Which role?** For each person, name the role (sponsor, operator, blocker, ghost, upstream
producer, system owner, eval owner, champion, sceptic, own side) and what they could do to stop the
work.

(a) The hospital's medical superintendent who signed the Kaagaz contract for discharge summaries.
(b) The insurer's third-party administrator who rejects pre-authorisation requests.
(c) The ward nurse who writes the discharge notes the system will read.
(d) The hospital's IT contractor who runs the 2014 HIS and its nightly backup.
(e) The senior physician who says "no machine summarises my patients".
(f) The resident doctor who keeps a WhatsApp group of pending pre-auths and asks when she can try it.
(g) Kaagaz's product lead who wants to know if a second hospital would buy this.

<details><summary>Solution</summary>

(a) sponsor; funding. (b) ghost; a rejection or a finding, never in the room; proxy is the
hospital's billing head. (c) upstream producer; input quality (incomplete notes). (d) system
owner; slowing. (e) sceptic, and probably an eval owner; ignoring, and a list of test cases. (f)
champion (owns a workaround, asks when she can try it); ignoring. (g) own side; funding. Day 42
draws this map in full. (Sections 02, 05.4.)

</details>

**1.2 Whose version?** Each sentence was said at Godavari. Say who said it, which row it fills,
and what it would need to be true.

(a) "Nine days has to become three."
(b) "We wait three days for the branch to resend a document."
(c) "Where does the PDF go?"
(d) "Three vendors have broken this system before."
(e) "Credit-ops sends files back for no reason."
(f) "Show me the decision, who made it, and the documents it rested on."

<details><summary>Solution</summary>

(a) the COO, sponsor; needs analyst time to be the bulk of the nine days (it is not). (b) the
analysts, operators; needs waiting to be the bulk (it is). (c) the CISO, blocker; needs a data
flow with every hop named before any file moves. (d) the core-system owner, system owner; needs
the vendors' failure modes to be knowable (they are: retries without idempotency, a stale sandbox).
(e) the branch managers, upstream producers; needs send-backs to carry no reason (they carry a
free-text one, which is why day-one feedback with the rule that fired is the fix). (f) the RBI
auditor, ghost; needs a human decision and a trail per file. (Section 03.)

</details>

**1.3 Place them.** Score power and interest for each and name the quadrant: (a) a bank's head of
internal audit who has not heard of the project; (b) a call-centre agent who will use the tool
six hours a day; (c) the CFO who approved the budget and has moved on; (d) the vendor-management
team that runs procurement.

<details><summary>Solution</summary>

(a) P5 I1, keep satisfied; a ghost-like row with a proxy; the quiet-veto risk. (b) P2 I5, keep
informed and listening; stops it by ignoring; must change. (c) P5 I2, keep satisfied; the sponsor
who funds and has lost interest, which is its own risk: re-score before the renewal. (d) P4 I2,
keep satisfied; stops it by slowing; met by week 2 with the questionnaire. (Section 04.1.)

</details>

## Level 2: apply

**2.1 The thirty-minute drill (out loud).** With a partner playing the core-system owner (give them
section 08.6's persona prompt, or play it from the admin script's "listen for" column), run the
admin and IT script against a timer. Record it. Afterwards, list every condition they gave you and
check it against the constraints list in the filled map. Which did you fail to ask for? Would they
have told you about the batch window unprompted?

<details><summary>What good looks like</summary>

Within thirty minutes: the systems and their owners by name, the batch and refresh times, the
three failed vendors and what each got wrong, the conditions verbatim (masked only, on-prem or
Mumbai, no vendor credentials, no PII out, no training), how a service account is approved, and
who gets the audit letter. The usual miss is the quarterly sandbox refresh, because nobody asks
"when does each run its refresh". The second usual miss is reading the conditions back. (Section
06.3.)

</details>

**2.2 The sponsor drill (out loud).** Partner plays the COO. Run the sponsor script. The partner's
brief: answer "nobody, I have approved it" to "who could stop this?", and "the system will tell
us" to "who decides whether a file is correct?". Your job is to handle both without contradicting
him in the first sentence.

<details><summary>What good looks like</summary>

"Nobody can stop it" becomes "then let me make sure that stays true: who signs the security review
and who gets the RBI letter, so I can meet them before they hear about this from someone else?"
"The system will tell us" becomes "it will tell us how fast; for whether a field is right I need
the person who would have typed it, because the auditor will ask who said it was right. Who is that
here?" Both move the sponsor from a wrong answer to an introduction without making him wrong.
(Section 06.4.)

</details>

**2.3 Predict the output (tested).** Before running, say which checks will fire if you make these
edits to `data/godavari-stakeholders.csv`: (a) blank the auditor's `proxy`; (b) change the CISO's
`first_contact_week` to 6; (c) change the analysts' `their_version` to the COO's sentence; (d)
change the identity team's `category` to "IT". Then run and compare.

<details><summary>Solution</summary>

(a) `S12 RBI auditor: a ghost with nobody named to speak for them in the room`. (b) two warnings
for S07: `can stop the work (veto) but first contact is week 6` and `high power, low interest, not
met in week 0 or 1: the quiet veto risk`. (c) `S01 and S04: the sponsor's version and an
operator's version are word for word the same`. (d) no warning: "IT" is not one of the checked
categories and the map still has a blocker and a system owner elsewhere; this is the floor, not
the ceiling, which is why the review checklist exists. (Section 08.4.)

</details>

**2.4 Break it, then fix it (tested).** The script treats a stakeholder with `stops_it_by` of
`finding` as exempt from the "met by week 2" check, because a ghost is never met. Add a row for an
internal audit team with `stops_it_by` = `finding`, `first_contact_week` = 9 and no proxy, category
"blocker (internal audit)". Run it. What should have fired and did not? Fix the script so that only
rows whose category starts with "ghost" are exempt, and rerun.

<details><summary>Solution</summary>

Nothing fires: the exemption is on the `stops_it_by` value, so a blocker who issues findings and
can be met slips through. The fix is one condition in `checks`: replace `p.stops_it_by != "finding"`
with `not p.category.lower().startswith("ghost")` in both places. After the fix the new row warns
`can stop the work (finding) but first contact is week 9` and `high power, low interest, not met
in week 0 or 1`, assuming you scored it P4 I1. The lesson is the same as section 09.3's last row:
the checks encode one engagement's shape, and a new kind of stakeholder needs a new check.

</details>

**2.5 The collisions you did not list.** The map has six collisions. Write two more, each with
who decides and when: one between the Vijayawada team lead (champion) and the forty analysts, and
one between the compliance head and the core-system owner.

<details><summary>Solution</summary>

Champion against analysts: she wants the tracker replaced by the review queue; the analysts fear
losing the tracker before the tool works. Decided by the team leads with the FDE in enablement:
the tool reads and writes the tracker before replacing it (Day 7's step 3 row; Day 33). Compliance
head against core-system owner: she wants the completeness rules changed by notification when
RBI amends the Master Direction; he wants no change to the core system's data model or batch.
Decided by the FDE's design, with both: the rules live in signed code outside the core system and
only the create call touches it (Day 11, Day 16). (Section 04.4.)

</details>

## Level 3: review and own

**3.1 Review this AI-written map.** Read [`worksheet/ai-draft-stakeholder-map.md`](worksheet/ai-draft-stakeholder-map.md)
and run the script on `worksheet/ai-draft-stakeholders.csv`. The script raises nine warnings. Find
at least ten problems in total, and say which the script caught and which needed you.

<details><summary>Solution (at least twelve)</summary>

Caught by the script: (1) no ghost: the RBI auditor is missing; (2) no upstream producer: branch
managers appear only as "end users" who need "app downloads"; (3) no system owner: the 2009 core
lending system and its owner are absent, "IT helpdesk" is not him; (4) no eval owner: nobody is
named whose judgement defines correct; (5) the users' engagement plan is "training session at
launch", a phrase; (6) the helpdesk's version is "raise a ticket", not their words; (7, 8, 9) the
CTO's sentence is word for word the users', Lakshmi's and the branch staff's: one interview, five
rows.

Needing a human: (10) the sponsor is the CTO; the notes say COO, and the "Head of AI" does not
exist; (11) the CISO is scored P2 I1 and "informed at UAT in week 8": she is a 5 on any map with
customer data, and a veto met in week 8 is a refusal; (12) Lakshmi is "appointed champion by the
CTO" with power 5: a champion is found, an appointed one is a liaison, and an analyst's power is
not 5; (13) the compliance head is missing entirely, so "no customer PII leaves India" never enters
the constraints list; (14) "no conflicts were identified" on an enterprise problem means nobody but
the sponsor was interviewed; (15) "the CTO will make the final decision" on all disputes: a sponsor
cannot overrule a regulator's condition; (16) the recommendation names a technology ("RAG chatbot
to all 300 branches") in a stakeholder map, which is Day 4's chatbot trap and Day 7's anti-pattern
in one line; (17) "user resistance" is a character word for a group whose day changes and who have
not been asked what they want. (Sections 08.6, 08.7.)

</details>

**3.2 Your own map.** Take a project you worked on (any employer, any domain) and draw its
stakeholder map from memory with the template: at least eight rows, verbatim versions where you
remember them, the collisions, the calendar. Then answer in writing: which row did you not know
existed at the time, and what did it cost? Keep the answer; it is a behavioural-round story (Day
45: "tell me about a stakeholder you missed").

<details><summary>What good looks like</summary>

The honest version of this exercise has a ghost or a system owner you met in month three. Most
engineers' first real map has one. The story is the cost ("a four-week rebuild of the export
because the data-protection officer had a retention rule we never asked about") and the change in
habit ("I now ask who gets the letter in week 0"). That is the shape the behavioural round scores.

</details>
