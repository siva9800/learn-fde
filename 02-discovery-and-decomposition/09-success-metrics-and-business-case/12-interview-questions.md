# 12 · Interview Questions

> Day 9 · Section 12 of 14 · [Chapter overview](README.md) · Previous: [11 · Mistakes and debugging](11-mistakes-and-debugging.md) · Next: [13 · Exercises](13-exercises.md)

---

Twelve questions in the forms they take in FDE loops: "how would you measure success?" inside the
decomposition round, "tell me about a business case you built" from the hiring manager, and "the CFO
does not believe your numbers" in the client simulation. Answer out loud first, then compare.

**Q1. The sponsor says "make it faster". What do you do with that?**

Turn it into a metric with a clock, a population and a baseline: for a lender, days from the
customer's signature to the decision, all files, withdrawn ones included. Then the ladder under it:
operational metrics that move it (hours per file, queue age, send-back delay) and system metrics that
move those (field accuracy, completeness recall and precision). The headline is the business metric,
never the model metric. (02, 03.2.)

**Q2. The customer already reports turnaround. Why measure it yourself?**

Because a report is a number with a method I have not read: what it counts (the core's received date,
not the signature), what it leaves out (withdrawn files), how much it would move if counted again, and
what it cannot see. A two-week hand count answers all four before the system touches a file, and it
cannot be done afterwards. At the course's lender it confirmed the report and found that six of nine
days were queue. (03.1, 03.7.)

**Q3. How would you draw the sample?**

Frame from the source that cannot forget a file (the SFTP log, not the core or the tracker); strata
that differ (branch cluster and product); proportional allocation with a floor of two; a seeded draw;
the list fixed before anyone opens a file; no replacements or re-draws; a second counter on 10
percent. About 120 files from 700 gives roughly plus or minus 8 points on a 30 percent rate. (03.4, 03.5.)

**Q4. Explain a confidence interval to a COO.**

"Our best estimate is 9.1 days, and the true figure for those files is very likely between 8.7 and
9.7. Below about 8.5 in the pilot is a real change; above it we will not claim anything." The interval
covers the luck of the draw, not a wrong definition or a frame that lost files. (04.1, 04.6.)

**Q5. How do you turn analyst hours into rupees?**

A loaded cost (everything that changes with one analyst fewer, allocations excluded, divided by
productive hours), and then the distinction people skip: freed hours are capacity, and become cash
only through hires not made, overtime avoided or attrition not replaced. Hours times a rate is not a
saving. (05.2, 05.4.)

**Q6. The system frees 12,000 hours a year. Is that 55 lakh of value?**

Only if the customer would otherwise hire. If the hours shorten the queue instead, the value is what
faster turnaround is worth, such as customers who no longer walk away. The same hours cannot do both,
so I show a capacity plan (hires made against queue days) and the sponsor chooses the split. (05.5.)

**Q7. What does a wrong decision cost a lender?**

A bad loan (extra default probability x exposure x loss given default), a regulatory finding (odds x
penalty, remediation and management time), a lost customer (lifetime contribution), each as an
expected value with visible inputs. The system's own errors are priced too: a missed document costs
a finding, a false flag three days of the customer's time, an unneeded review a few minutes, which is
why completeness rules favour recall. Disbursement pulled forward is not on this list: it happens once.
(06.1 to 06.3.)

**Q8. Your measured lever does not pay for the system. What goes on the page?**

The floor (the case on measured levers alone: minus 1.12 crore a year at the course's lender); the
break-even on the unmeasured lever in words the sponsor can judge ("keep about three in ten of the
customers who walk away today"); that lever as the pilot's first question; and the commercial options
left to the commercial people. Inflating the capture share to close the gap is how the CFO stops
trusting every other number. (07.2, 07.3.)

**Q9. What is a sensitivity table for?**

It moves one assumption at a time to show which inputs matter. The usual lesson: the number everyone
argues about matters least. At the lender the loaded rate moved the case by 13 lakh, the untested
walk-away assumption by 1.9 crore, so that is what the pilot measures. (07.4.)

**Q10. Which numbers get gamed, and how do you prevent it?**

Clock starts, resubmissions resetting the clock, withdrawn files dropped, pilots in easy branches,
self-reported hours, accuracy on easy fields or on the set the prompts were tuned on, send-backs falling
because nobody sends files back, samples re-drawn until they agree. Mostly honest choices made after
seeing the data. Prevention is pre-registration, signed by the sponsor and the compliance head before
the pilot, with a guardrail paired with each target. (08.)

**Q11. How does the eval metric connect to the business case?**

Through the capture share: analysts stop re-typing a field only when it is almost always right. I
register the link as an assumption (95 percent field accuracy, 60 percent capture; below 90, 30) and
name the accuracy below which the case fails. That makes the golden set the case's first checkpoint,
months before a business number moves. (08.5; Day 14.)

**Q12. A CFO says "I do not believe your numbers". What do you say?**

"Which one?" Then that number's method (frame, sample, interval, signed definition) and its row in the
sensitivity table, which shows how much it matters. If it is an assumption, I say so, show the
break-even and how the pilot measures it. A case built so that every number can be challenged is
working when it is challenged. (07, 08; Day 30 for the bad version.)
