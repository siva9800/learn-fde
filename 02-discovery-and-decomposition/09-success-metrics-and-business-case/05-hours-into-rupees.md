# 05 · Hours Into Rupees, Honestly

> Day 9 · Section 5 of 14 · [Chapter overview](README.md) · Previous: [04 · Confidence intervals](04-confidence-intervals-in-plain-words.md) · Next: [06 · The cost of being wrong, and of the system](06-the-cost-of-wrong-and-of-the-system.md)

---

## 5.1 Day 4's placeholder

Day 4 used 300 rupees per analyst hour, "roughly a 6 lakh a year loaded cost over 2,000 working
hours", and marked it as a placeholder for today. It was really a salary rate: 6 lakh is an
analyst's CTC, and CTC is not what an analyst costs Godavari. This section replaces it, then explains
the harder point: even the right rate does not turn hours saved into rupees saved.

## 5.2 Fully loaded cost: what counts and what does not

The **fully loaded cost** of an analyst is everything Godavari spends because that seat is filled,
and would not spend if it were empty. The test for each line is one question: **would this cost
change if Godavari had one analyst fewer?**

| Line (per analyst per year, invented) | Rupees | Counted? | Why |
|---|---|---|---|
| CTC (includes employer PF and gratuity) | 6.00 lakh | yes | the payroll cost of the seat |
| benefits outside CTC (medical cover, bonus) | 0.45 lakh | yes | paid per head |
| seat and facilities, Hyderabad and Vijayawada | 0.75 lakh | yes | a seat not filled is not rented |
| IT, laptop, licences | 0.35 lakh | yes | per head |
| supervision share (two team leads, half an ops manager) | 1.08 lakh | yes | spans of control grow with heads |
| attrition: hiring and training replacements | 0.50 lakh | yes | 25 percent attrition at about 2 lakh a replacement |
| HQ overhead allocation (finance, HR, the board) | 0.90 lakh | **no** | the same with 40 analysts or 47 |
| the core system and its licence | 0.60 lakh | **no** | runs whatever the headcount |

Counted lines total **9.13 lakh**. Divided by **2,000 productive hours** (about 290 working days at
eight hours, less leave, less 5 percent for meetings and training), that is **456 rupees an hour**,
about one and a half times Day 4's placeholder. CTC alone over the same hours is 300; the placeholder
was the salary rate all along.

Three rules: divide by **productive** hours, not paid hours (about 2,300), or you overstate what an
analyst has to give; **allocations are not costs**, so if finance insists on a fully absorbed rate,
show both and use the marginal one; and **ask finance for the number**, keeping your build-up as the
check. Every line above is invented; Godavari's finance controller has the real CTC bands.

## 5.3 The problem's cost and the system's share are different numbers

With the measured 1.59 addressable hours a file:

```text
the problem's cost:  16,800 files x 1.59 h x 456 = 1.22 crore a year   (Day 4's question: is it big enough?)
the system's share at 60% capture: 0.73 crore of capacity   (Day 9's question: how much, and is it cash?)
```

Day 4 asked whether the problem is big enough for a 1.2 crore subscription, and the answer holds,
just. Day 9 asks how much of it the system removes. An analyst still opens the file, reads the
fields, corrects some and approves, so the **capture share** (the fraction of addressable hours
actually removed) is an assumption until the golden set measures accuracy (08.5). Quoting the size of
the problem as the value of the solution is the commonest error in AI business cases.

## 5.4 Capacity is not cash

0.73 crore of analyst time freed is **capacity**: forty people with more time. It becomes cash only
when Godavari spends less money because of it. There are three ways that happens, and one way it does
not.

| How freed hours become rupees | At Godavari |
|---|---|
| **hires not made** | the COO's plan has 18 percent more files next year; without the system that needs about seven more analysts |
| overtime or temporary staff not paid | month-end pushes; small at Godavari |
| attrition not replaced | possible; slow, and the analysts will hear about it |
| ~~analysts released~~ | not on the table, and saying it in week three would end the engagement on the floor (Day 33's adoption depends on the analysts trusting you) |

So the honest rupee value of freed hours is **the loaded cost of the hires not made**, not hours
times rate. If Godavari would not have hired anyone, the freed hours are worth what they are spent
on, which brings us to the second rule.

## 5.5 The freed hours are spent once

The same hours can cut the queue or avoid a hire. They cannot do both.

Why the queue depends on hours: forty analysts with 2,000 productive hours each have 80,000 hours a
year. Today's 16,800 files at 4.6 hours need about 77,300. **Utilisation is 96.6 percent.** Queueing
theory's standard result (Kingman's approximation) says that waiting time grows with
utilisation / (1 - utilisation): at 0.966 that factor is about 28; at 0.84 it is about 5. That is why
files wait six days in a queue at Godavari although each one takes a day and a half of work, and why
a modest cut in hours per file can cut the queue by days. It is also why the queue is so sensitive at
month-end (three times the volume, Day 6) and in March.

The script turns this into the capacity plan the COO has to choose from. With the system at 60
percent capture and next year's volume:

```text
  hires made  utilisation  queue days  median days  hires avoided  capacity cash
           0        90.3%         2.1          4.5            7.2      65.7 lakh
           1        88.1%         1.7          4.1            6.2      56.6 lakh
           2        86.0%         1.4          3.8            5.2      47.5 lakh
           3        84.0%         1.2          3.6            4.2      38.3 lakh
           4        82.1%         1.0          3.5            3.2      29.2 lakh
           5        80.3%         0.9          3.4            2.2      20.1 lakh
           6        78.5%         0.8          3.3            1.2      11.0 lakh
           7        76.9%         0.7          3.2            0.2       1.8 lakh
```

Hire nobody: save 66 lakh, median 4.5 days. Hire three: save 38 lakh, median 3.6. Hire all seven:
save nothing, median 3.2. The COO's "three days" and the CFO's "save money" pull against each other,
and the table makes that a decision. The case assumes three hires. Two cautions: the queue line is
calibrated to the measured 6.4 days at 96.6 percent with an approximation described as "generally
very accurate, especially for a system operating close to saturation" (section 14), ignoring
month-end peaks; and the median also assumes day-one detection lets the branch's three-day wait run
in parallel with the shorter queue. Both are hypotheses the pilot tests.

## 5.6 Hours the case must not count

Credit assessment (not addressable), branch staff and customer time (real, but not this budget;
list them), meeting time (a cost, section 06), and any hour already counted once.

## 5.7 Key takeaways

- Loaded cost counts every line that changes with one analyst fewer, divided by productive hours:
  456 rupees an hour at Godavari, against Day 4's salary-based 300.
- The problem's cost (1.22 crore) is not the system's value (a captured share of it).
- Freed hours are capacity; they become cash through hires not made, overtime avoided or attrition.
- At 96.6 percent utilisation, small cuts in hours make large cuts in queue. The freed hours are spent
  once: on the queue or on hires, and the COO chooses the split.
