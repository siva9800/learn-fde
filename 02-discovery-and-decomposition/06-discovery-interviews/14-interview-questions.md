# 14 · Interview Questions

> Day 6 · Section 14 of 16 · [Chapter overview](README.md) · Previous: [13 · Mistakes and debugging](13-mistakes-and-debugging.md) · Next: [15 · Exercises](15-exercises.md)

---

Thirteen questions in the forms they take in FDE loops: the hiring-manager screen ("how did you run discovery?"), the behavioural round ("tell me about a time"), and the follow-ups inside the decomposition and client-simulation rounds. Answer out loud, then compare.

**Q1. Walk me through your first two weeks at a new customer.**

Days one and two are access and reality: every ticket raised on day one with its reason (building, shadowing permission, documents, the document store, a sandbox, a folder for my notes), because each has a clock, and a check of every sentence the sales notes made about SSO, the data and the APIs. Then I shadow operators for full units of work and interview 8 to 10 end users across roles and locations, plus the admins who own access and rules and the sponsor once, before any production code. I code the notes every evening, synthesise every three or four interviews, and by the end of week two I have the workflow as it actually runs, reviewed with the operators, and the findings that change the architecture. (Sections 02 to 10.)

**Q2. Why shadow? Why not just interview?**

Because people describe the system and do the job, and the two differ. Shadowing shows the real first step, the windows open at once, the waits in minutes, the re-keying, the notebook and the WhatsApp page arriving mid-task. At a lender I watched an analyst open a spreadsheet before the core system, every time; the SOP's twelve steps were nineteen on the floor. It also makes the afternoon interview honest: someone who has watched you count without judging tells you what she skips on a bad day. (Section 03.)

**Q3. How many people do you interview, and how do you choose them?**

At least 8 to 10 end users, which is what the 2026 discovery playbooks say, plus every blocker and the sponsor. I build the roster from the stakeholder map, not the sponsor's introductions: the most experienced and the newest operator, both locations, the sceptic, the upstream producers near and far, and each admin whose rule could change the design. The number matters because I treat a finding as a requirement only when three independent interviews support it. (Section 04.)

**Q4. Give me three questions you always ask operators.**

"Show me the last one you did." "What do you do when it is wrong?" "What is in the Excel sheet?" The first gives the real steps, the second gives who corrects errors and what they fear, the third gives the shadow system. All three ask about a specific instance or artefact, which is why they get true answers. (Section 05.1.)

**Q5. How do you avoid leading the witness?**

I never say my hypothesis aloud. I ask about the last instance, follow every adjective to a number, count to five after an answer, ask for the artefact, echo their phrase instead of interpreting it, and get the full sequence before asking why. And I read my notes back at the end; leading shows up as people agreeing with sentences they did not say. (Section 06.)

**Q6. What questions change the architecture?**

Who may see what, and where that rule lives. How access is granted and how fresh it is. Where the input comes from and when. What must never be automated. Who corrects errors today. What happens when it is wrong. At a lender, the first one produced the requirement that retrieval filter by the caller's directory groups at query time, because branch managers must not see each other's files and the groups come from HR nightly. Asked in week two it is a requirement; found in week eight it is a re-index and a lost CISO. (Section 08.)

**Q7. Tell me about a discovery finding that changed a design.**

(Use the STAR shape, in the first person.) "At a lender, the team lead mentioned, in passing, that he could not see a colleague's queue while she was on leave until IT added him by hand. I asked the CISO and the core-system owner where that rule lived: directory groups from HR, synced nightly, no 'all branches' group, and she wanted a seven-year view log. I wrote it as a requirement in week two: every query carries the caller's groups at query time, the service account holds nothing global, every view is logged. It went into the security questionnaire as a diagram. Building retrieval without it would have meant a re-index in week eight." (Sections 08.2, 08.3.)

**Q8. The customer has an Excel tracker that runs the operation. What do you do with it?**

Treat it as a requirement, not a workaround. Its columns are the states the official system lacks; its owner is my likely champion. I read it before I replace anything, plan to write state back so there is one record, and never describe it to the sponsor as a failing of the operators. Three vendors at that lender had promised "you will not need the spreadsheet"; the analysts kept it, and the vendors left. (Section 09.)

**Q9. How do you turn ten interviews into findings?**

Code each quote the same evening with a reusable code, a verbatim quote and a kind. Tally codes by independent interviews. Three or more is a requirement; fewer is a hypothesis to test in the skeleton, unless a test has already confirmed it. Write architecture findings first, then constraints, scope, and a section on what was not found. Check both directions: no finding without a transcript, no requirement left out. Then review it with the operators before the sponsor sees it. (Section 10.)

**Q10. Would you use an AI assistant for discovery?**

Yes, for preparing scripts and for a first grouping of coded notes, with the transcripts allowed under the customer's data rules. The failure I design around is invented findings: an assistant synthesising interviews writes what lenders usually have and sponsors usually want, such as "analysts would welcome a chatbot" or "the core has a REST API", in the same confident voice as the real findings. So every finding must cite codes from the transcripts, a script checks that, and I read every quote behind section A myself. (Section 12.5.)

**Q11. The sponsor says "just talk to my two team leads; they know everything." What do you do?**

Talk to them first, and ask each who would tell me this will fail and who is newest. Team leads know the queue, not what the newest analyst skips or what the far branch photographs. I frame the three-interview rule as protecting his project. If I still get only two, the empty rows go into the plan as a risk and I shadow harder. (Sections 04.6, 11.3.)

**Q12. In a client simulation, an operator says: "Three vendors have come. Each said we would not need the spreadsheet." Respond.**

"Then I will not say it. Can you show me what the spreadsheet does that the core system does not? If what we build cannot do those things, you should keep the spreadsheet, and I would rather know that in week two." Then I ask to see the columns and the colours. It acknowledges the history, makes no promise, and turns the objection into requirements. (Day 34 runs the full role-play.)

**Q13. How do you know discovery is done, and what is the map you hand over?**

When the map is reviewed and signed by the operators, every architecture-kind requirement has a home in the decomposition, the hypotheses are listed as tests for the walking skeleton, the golden examples and their labellers are named, and new interviews stop producing new codes. Discovery is never fully done; the map is versioned at each checkpoint. (Sections 09.4, 10.5, 11.3.)

## Quick-fire

- Minimum end users before production code? 8 to 10. Threshold for a requirement? Three independent interviews.
- Who reviews the map first? The operators who gave it to you.
- How many golden examples, and who builds the set? 100 to 200; Day 14.
