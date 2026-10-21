# 10 · Interview Questions

> Day 5 · Section 10 of 12 · [Chapter overview](README.md) · Previous: [09 · Mistakes and debugging](09-mistakes-and-debugging.md) · Next: [11 · Exercises](11-exercises.md)

---

Twelve questions in the forms they take in FDE loops: the hiring-manager screen ("how do you run
discovery"), the pushes inside the decomposition round ("who else?"), and the client-simulation
round ("the CISO has just said no"). Answer out loud first, then compare. Section numbers point to
the full explanation.

## The roles

**Q1. Who are the stakeholders in an enterprise deployment, and how do you find them?**

By what they can do to the work, not by title: the sponsor, who funds it and wants a number; the
operators, whose day changes and who can quietly ignore it; the blockers, who can say no on behalf
of security, compliance, legal or IT; and the ghosts, who are never in the room and can stop
everything with a finding, like a regulator or an auditor. Then the three everyone misses: the
upstream producer of the input, the owner of the system we write into, and the eval owner whose
judgement defines a correct output. I find them by reading the organisation rather than the chart:
who is cc'd and silent, who owns the spreadsheet, who approved the last vendor, who gets the audit
letter, who says "we tried that". And I put my own side on the map. (Sections 02, 05.2.)

**Q2. The sponsor says the analysts are slow. The analysts say they are waiting on the branches. Who is right?**

Both, from where each sits, and the job is to hold both rather than pick one. The sponsor sees
forty salaries and a nine-day number the core system reports; the analysts see a tracker row that
says "waiting on bank statement since Tuesday", which the sponsor has never opened. I record both
verbatim, ask what each would need to be true, test it by shadowing and a baseline sample, and look
for the lever that moves both numbers. On a lender's loan intake that lever was a completeness
check on day one: it cuts the sponsor's turnaround and the analysts' chases at once. Then I write
the one sentence both will sign. (Section 03.)

**Q3. Who decides whether the system's output is correct?**

Not the sponsor. The person who would have done the work by hand and knows what wrong looks like:
a senior analyst for extracted fields, the compliance head for whether a file is complete, the
auditor, through her, for whether a decision is reviewable. The 2026 discovery playbooks call this
the eval owner and are explicit that they are usually not the sponsor. I name them on the map in
week 0 and say to the sponsor, in those words, "you decide how fast it has to be, they decide what
counts as right, and we measure both." If the sponsor defines correct, the golden set is labelled
against the demo and the first audit finding is mine. (Section 03.3.)

**Q4. What is a ghost stakeholder, and give one from an engagement.**

Someone never on the invite list who decides what is acceptable: the RBI auditor at an NBFC, the
insurer's TPA at a hospital, a state regulator for a utility. Their version of the problem is never
said in the room because to the people inside it is the weather; I write it anyway, in their
voice ("show me the decision, who made it and the documents it rested on"), and I name a proxy, the
person who gets the letter, who speaks for them. The auditor's row alone changes three layers of the
first slice: a human decision per file, an audit trail that survives a model upgrade, and no
automation of the completeness rules without a signed version. (Sections 02.1, 03.4.)

## Power and interest

**Q5. How do you use a power-interest grid, and what does it get wrong?**

Score each row 1 to 5 on power (what they can do to the outcome) and interest (how much their day
depends on it). Four quadrants with a default: manage closely, keep satisfied, keep informed and
listening, monitor. The veto quadrant, high power and low interest, is where the week-1 meetings
go. What it gets wrong is the operators: forty analysts score 2 on power and hold the only power
that matters after go-live, whether the tool is used. So I add two columns: "stops it by" (funding,
veto, slowing, ignoring, input quality, a finding) and "must change". The people who can stop the
work and the people who must change their behaviour are mostly different, and the second group
needs more of my time. (Sections 04.1, 04.2.)

**Q6. Who signs, who can veto, who opens the tool: why three lists?**

Because confusing them is how engagements die. The sponsor signs the plan and the scope; the
CISO, the compliance head and the core-system owner can veto, each on behalf of something bigger
than the project; the operators open the tool or do not. Treating a team lead's enthusiasm as a
signature leaves the plan without an owner when it slips. Treating the sponsor's approval as the
CISO's leaves a ten-week build with no deployment. Measuring success as a demo the sponsor loved
leaves adoption to be discovered in month four. Nobody should be on all three lists on an
enterprise problem. (Section 04.3.)

**Q7. Give me a conflict between two stakeholders and say who decides it.**

The sponsor's turnaround number improves most if clean files are auto-approved; the auditor
requires a human decision on every file. The compliance head decides, for the auditor, and the
sponsor cannot overrule her; the first slice obeys the auditor and the question goes on the readout
agenda. The general rule: when a sponsor's want collides with a blocker's or a ghost's condition,
the condition wins and the collision becomes an agenda item with a date. A map with no collisions
involving the sponsor has only interviewed the sponsor. (Section 04.4.)

## Blockers, champions, the calendar

**Q8. The security head said no to everything in week one. What do you do?**

Thank her, because a blocker met in week one writes conditions and one met in week ten writes a
refusal. I tell her I have nothing to show and would rather not build what she will have to refuse,
and I ask for the conditions under which a vendor's system may touch a loan file: where it may
run, who may hold credentials, what never leaves the country, what is never trained on. I write
every sentence verbatim, read it back, and start the questionnaire the next week. Her row on the
map is filled by her. The same move works on the compliance head and the system owner. (Section 05.3.)

**Q9. How do you find a champion, and why not let the sponsor appoint one?**

Three tests: they own a workaround (the spreadsheet that is the real state), they describe the
problem in their own numbers, and they ask when they can try it rather than when it will be ready.
At the lender it was the team lead who kept the tracker alive by hand. A champion the sponsor
appoints is a liaison, useful and different: they relay, they do not defend the tool on the floor
when I am not there. The sceptic is the other adoption row: I interview her for her failure model,
which is a list of test cases, and do not try to convert her; the pilot workshop where the tool
flags her handwritten income proofs instead of guessing is what converts her. (Section 05.4.)

**Q10. What on the customer's calendar changes your plan?**

The regulator's inspection, when the compliance head disappears for weeks and nothing goes live;
the core system's release freeze at quarter end, when no integration can land; the financial year
end, when the sponsor's number is reported; festival weeks, when half the operators are on leave;
month end, when hours per file are not comparable. I ask the sponsor and the system owner for these
in week 0, put them on the map, and sequence the 90-day plan around them. The sponsor will not
volunteer them because to him they are obvious. (Section 05.5.)

## The method and the tooling

**Q11. How does the stakeholder map feed the rest of discovery?**

It decides whom I shadow and interview in week one, because the operators and the eval owners are
on it by name. It starts the constraints list ("no PII leaves India" is a sentence on the map
before it is a requirement anywhere), which decomposition takes as the things that cannot move. It
gives the decomposition step a row per person to attach a metric to. It lists the collisions that
become the readout agenda, and it says who must be in the readout room for the document to be
signed rather than admired. And it is versioned: the week-0 map beside the current one is a record
of what I learned. (Sections 01.3, 07.3.)

**Q12. You asked an AI agent to draw the map. What do you check before you trust it?**

That every row traces to a line in my own notes and not to the agent's idea of an enterprise: it
invents a CTO or a "Head of AI" as sponsor. That the operators are not one row called "users" with
one sentence; if the sponsor's sentence and the users' sentence are the same words, one of them was
never interviewed. That the ghost and the upstream producer are present. That power was scored from
what people can do to the work, not from the org chart (the CISO is a 5 on any map with customer
data on it). That the blockers are met by week 2, not "at UAT". That there is at least one
collision with the sponsor on one side and a decider who is not the sponsor. And that nothing in
the map would surprise the person it describes. (Section 08.6.)

## Quick-fire

- **Sponsor, in one line?** Funds it, wants a number, can stop it by withdrawing either.
- **Operators' power?** Ignoring. Silent and expensive to reverse.
- **Blocker versus ghost?** A blocker is in the room and can say no; a ghost is never in the room and can issue a finding.
- **The three everyone forgets?** Upstream producer, system owner, eval owner.
- **Eval-customer split?** The buyer and the judge of correctness are different people; name the judge.
- **When to meet the CISO?** Week one, for conditions.
- **Champion test?** Owns a workaround, has their own numbers, asks when they can try it.
- **Sceptic?** Interview for the failure model; it is a list of test cases.
- **What wins a collision?** A blocker's or ghost's condition over a sponsor's want; then the readout.
- **One rule for what goes in the map?** Nothing a person would be surprised to read.
