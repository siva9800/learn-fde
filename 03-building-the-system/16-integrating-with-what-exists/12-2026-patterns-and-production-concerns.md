# 12 · 2026 Patterns and Production Concerns: MCP, CDC, Facades, and What Is Hype

> Day 16 · Section 12 of 18 · [Chapter overview](README.md) · Previous: [11 · The reconciliation report](11-the-reconciliation-report.md) · Next: [13 · Project: the Godavari integration layer](13-project-the-godavari-integration-layer.md)

---

## 12.1 What practitioners use in 2026

Library and protocol names below are current as of October 2026 and will date; the reasons will not.

| Pattern | What it is | When it is right at a customer like Godavari | When it is not |
|---|---|---|---|
| **Tool wrappers for the model** | read-only functions (Day 12's `lookup_core_application`, `get_tracker_status`) that call the port and return results through the translation layer | an analyst asks "where is file X?" and the answer is in two legacy systems | anything that writes: Day 12's rule, "the tool list is the permission list" |
| **MCP servers in front of legacy systems** | the Model Context Protocol exposes tools and resources to any MCP-capable client | one integration reused by several agents or IDEs | as the whole layer: OpenAI's FDE team, per the ZenML summary, treats MCP as "a starting point for data connectivity" and builds "additional logic layers between raw MCP connectors and LLM consumption"; idempotency, windows and masking still live in your code |
| **A facade (SOAP to REST or JSON)** | a small service that speaks the legacy protocol on one side and a modern one on the other | several consumers, and the customer's team will own the facade | when it becomes a second system nobody owns; the facade inherits every rule in this chapter |
| **Change data capture (CDC)** | streaming the core's changes from its database log (Debezium is the common open-source option) instead of a nightly copy | the owner agrees, the database supports it, and a day-old copy is too stale | a 2009 core with a DBA who has never heard of it, in week 3; the reporting copy is enough for intake |
| **iPaaS and the customer's own ESB** | MuleSoft, Boomi, an in-house enterprise service bus | the customer already runs one and has people for it: use theirs | buying one for the engagement |
| **Text-to-SQL over the metadata layer** | a model writes queries using the mapping's business names | ops questions across many files, on the reporting copy | without the authorizer: a model's SQL is untrusted input |

## 12.2 Coding agents and integration work

Agents are genuinely good at the mechanical parts of this chapter: reading a 61-field WSDL and drafting the
mapping skeleton, generating a client, writing a recorder, turning a fault catalogue into a table, writing
the hundredth parsing test. They are poor at the parts that need facts from the customer: which fields are
computed, what `CUST_FLG_3` means, the transaction ceiling, the batch window, the rate limit, which columns
the owner signed. Section 14 lists the specific mistakes; the pattern is that an agent fills a gap with a
plausible guess, and in an integration the guess is a duplicate loan or a leaked PAN.

## 12.3 What is hype

- **"AI makes integration obsolete."** The model still has to read from and write to the 2009 core, and
  the core still has no idempotency key. AI changes who writes the adapter, not whether it is needed.
- **"The model can infer what the fields mean."** It can guess that `CUST_FLG_3` is a flag. It cannot know
  that it means salaried, that gold loans send N, or that `CUST_FLG_4` must never be set by intake. Write it
  down (section 08).
- **"Just put an MCP server in front of it."** That moves the problem behind a new protocol. The rules in
  sections 04 to 09 still have to be somewhere, and they belong below the model, not in its prompt.
- **"Copy everything into a vector store and query it."** That is the data you are not allowed to copy
  (section 09), with a search box on it.
- **"Retries make it reliable."** Retries make reads reliable. For creates without keys they make
  duplicates.

## 12.4 Production concerns

**Latency.** A SOAP call to an on-prem core takes tens to hundreds of milliseconds; the client paces at
four a second because the core refuses six. Ten files are a few seconds; at month end, with three times the
volume (finding B3), the writer's throughput is set by the rate limit and the window, not by your code. Plan
the queue, not more workers. Twenty parallel workers, the AI-draft plan's suggestion, would trip CL-E099
on the first second.

**Scheduling.** Writes happen 08:00 to 17:30 and after the batch; reads any time; the pickup at 02:30 and
03:30; the reconciliation at 06:00; the report by 09:00. Sunday 06:00 to 09:00 is maintenance. Put these in
one schedule file, owned with the application-support engineer, rather than in five cron lines on five
machines.

**Monitoring.** The signals worth a dashboard (Day 19 builds it): UNKNOWN writes older than the quiet
period, DEFERRED writes after 20:00, CL-E099 counts, PARTIAL files at 04:00, the reconciliation's clean
flag, and the age of the reporting copy.

**Security and network.** The service account is issued through the CISO personally (finding B2) and starts
with no groups; the SFTP account is read-only with a pinned host key; the reporting account sees signed
columns only. Secrets live where Day 25 puts them, never in the repository; the stand-in's password says
`sbx-only-not-a-real-secret` so that nobody mistakes it for one.

**The cutover.** On 4 January 2027 (M16) the system moves to Godavari's VPC in AWS Mumbai, and the core
stays on-prem. Every call in this chapter then crosses the network path Day 25 designs, with its own
latency and its own failure modes; the four outcomes in section 03 do not change, which is the point of
having them.

**Handoff.** Day 28's question is whether Godavari's application-support engineer can run this without
Kaagaz. Plain-text mappings, a known-drift list with owners, a report written for the system owner, and a
runbook line per failure (section 15) are what make the answer yes.
