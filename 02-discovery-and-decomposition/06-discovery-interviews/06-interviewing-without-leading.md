# 06 · Interviewing Without Leading, and Notes That Are Evidence

> Day 6 · Section 6 of 16 · [Chapter overview](README.md) · Previous: [05 · The question bank](05-the-question-bank.md) · Next: [07 · The situational map](07-the-situational-map.md)

---

## 6.1 Why engineers lead, and how it shows

Engineers lead in interviews for a reason that is almost a virtue: they have already formed a hypothesis and they want to test it. The trouble is that a hypothesis spoken aloud to an operator becomes the answer. "So the delay is mostly the branch resending documents?" gets a nod from everyone, because it is partly true, because you are the vendor the COO brought in, and because disagreeing with a visitor is rude in most of the offices you will ever sit in. You leave with your hypothesis confirmed and no idea that a third of the send-backs are a junior being cautious because the acceptable-alternatives list is unwritten.

The tell is in your own transcript. Count the questions that contain the answer:

| Leading | What it assumes | Open |
|---|---|---|
| "So you spend most of the time waiting for the branch?" | that waiting is the lever | "Where did the days go on the last file that took long?" |
| "The tracker is basically a workaround for the core system, right?" | your interpretation of the tracker | "What does the tracker do that the core does not?" |
| "Would it help if the fields were already typed?" | the solution | "What did you type that was already typed?" |
| "Is the handwriting the hard part?" | which part is hard | "Which files take you longest, and why those?" |
| "You must get a lot of WhatsApp photos." | the frequency | "What came today by a route that is not in the SOP?" |
| "The 2019 pilot failed on handwriting, didn't it?" | the failure mode | "What did it get wrong, in as much detail as you remember?" |

The open versions are longer to answer and produce silences. The silences are the point.

## 6.2 Seven mechanics

| Mechanic | What you do | Why |
|---|---|---|
| **Specific, recent, concrete** | ask about the last instance, the one before lunch, the one that came back on Tuesday | memory of an instance is accurate; description of a process is a story |
| **Follow the adjective** | "slow" becomes "how many hours, measured how, by whom?"; "often" becomes "how many this month?" | adjectives are the sponsor's currency; numbers are yours |
| **Count to five** | after an answer, say nothing for five seconds | the second answer, the one after the pause, is the honest one: "on a bad day I check the big ones and hope" came after a pause |
| **Ask for the artefact** | "show me" instead of "tell me"; the tracker, the printed checklist, the phone, the notebook | artefacts do not round; the 2024 checklist in a 2025 world was found by asking to see it |
| **Echo, do not interpret** | repeat their last phrase as a question: "received by WhatsApp?" | it invites more without steering; interpretation ("so that is a workaround") invites agreement |
| **Separate what and why** | get the whole sequence first, then ask why about the parts that surprised you | asking why mid-sequence makes people justify instead of describe, and they skip the steps they cannot justify |
| **Ask what would have to be true** | for the sceptic: "what would have to be true for you to trust it on a printed slip?" | it turns an objection into a test case ("a hundred files I have done, with my figures, field by field") |

## 6.3 The sceptic, specifically

The published playbooks single out one conversation as "the highest-leverage hour of week 0": the person who expects the project to fail. The advice is not to convert them but to **extract their failure model**, and the mechanics above are how. The senior analyst in Hyderabad did not say "it will never work". She said, when asked for detail, "it typed four lakh eighty thousand as monthly; the sanction went through at ten times the eligibility; I caught it the next morning because the EMI looked wrong for an auto driver." That is a test case, an accuracy requirement, a confidence-routing requirement and a review-queue design in one paragraph, and it came from "tell me what it got wrong, in as much detail as you remember" followed by silence.

Three things not to do with a sceptic: do not defend the product ("our model is much better than 2019 OCR"); do not promise ("we will handle handwriting"); do not skip her because the sponsor said she is difficult. Her condition for trust ("show me a hundred files with my figures, not a percentage") became Day 14's output format.

## 6.4 Note-taking

Notes are evidence, and evidence has rules.

| Rule | Why | Example from the pack |
|---|---|---|
| **Verbatim quotes, in quotation marks** | a paraphrase carries your interpretation; a quote carries theirs; the readout will be challenged and the quote is your defence | "Me. Always me. If your system reads the slip and reads it wrong, it will still be me who is asked." |
| **Mark inferences as inferences** | "(I think this means the core file never gets the WhatsApp page)" in brackets, confirmed or struck at read-back | the inference about the core file was confirmed by three people and became a finding |
| **File numbers, not names** | DPDP; the CISO's rule; a lost notebook is not an incident if it has no PII | "two-wheeler, Kukatpally, 34 pages" |
| **Time-stamp the shadowing log, not the interview** | the log needs the waits; the interview needs the words | section 03 |
| **One code per finding, assigned the same evening** | a code (BRANCH_ISOLATION, SHADOW_TRACKER) is what lets ten transcripts be tallied | section 10 |
| **Record the question that produced the answer** | a quote produced by a leading question is worth less; your future self needs to know | the transcripts keep the FDE's lines |
| **Write what you did not hear** | "nobody mentioned a chatbot" is a finding, and the one an assistant will most want to invent | section D of the synthesis |

Two people in the room beats one when you can get it: one asks, one writes. On your own, write during the silences; the operator is used to people typing.

## 6.5 The read-back

The last five minutes of every interview are the read-back, and it is the single most reliable step in the method. You read your notes aloud, as sentences, and the interviewee corrects them. It does four things:

1. **It catches your errors while they are cheap.** Lakshmi corrected "typing takes 1.5 hours" to "1.5 hours including checking"; Srinivas separated the 02:00 transfer batch from the 18:00 credit batch; the Guntur manager put a number on "most" ("one in four normally"). Each correction would have been a wrong row in Day 7's table.
2. **It shows them you wrote down what they said, not what you wanted.** That is the trust the next interview runs on.
3. **It gives them a chance to add the thing they held back.** The Vijayawada team lead's "the tracker also has colours; nobody wrote that down anywhere" came in the read-back.
4. **It is the first confirmation step of the synthesis (section 10),** done while they are in the chair.

Read back facts and quotes, not conclusions. "You said the file sits three days, sometimes a week" is a read-back. "So the main problem is the branches" is a leading question wearing a read-back's clothes.

## 6.6 Interviewing across a language

Godavari's floor works in Telugu and English mixed, the branch managers in Telugu. If you share the language, interview in it and keep quotes as said, with your translation marked as yours. If not, ask the team lead to translate and accept losing the pauses. Never let the sponsor translate; you will get his version in two languages.

## 6.7 Key takeaways

- A hypothesis spoken aloud becomes the answer. Ask about the last instance, follow the adjective, count to five, ask for the artefact, echo rather than interpret, get the what before the why.
- Extract the sceptic's failure model; do not convert her. Her condition for trust is a test case.
- Notes are evidence: verbatim quotes, marked inferences, file numbers not names, one code per finding, the question that produced the answer, and what you did not hear.
- Read back facts and quotes in the last five minutes; the corrections are the most reliable numbers you get.
