# AI-written draft · "Godavari intelligent intake: target architecture"

> Exercise 3.2. An AI assistant was given the Day 10 discovery document and asked for "a modern, AI-first
> architecture for Godavari's loan intake, one page, for the COO". This is its answer, unedited. It is fluent
> and confident and has at least twelve problems. Find them before reading the solution in section 15.

---

## Overview

Godavari's intake will be powered by a single intelligent agent built on a frontier LLM. The agent reads each
loan file end to end, understands Godavari's policies, and makes the completeness decision, removing the
manual checklist entirely. Because modern models follow instructions reliably, all fourteen two-wheeler rules
and the RBI KYC requirements are provided to the agent in its system prompt, which compliance can update at
any time through an admin screen.

## Components

1. **Document AI.** Files are uploaded from the SFTP folder to the vendor's cloud OCR service in Singapore for
   best accuracy, then passed to the agent.
2. **Policy prompt.** A 6,000-word system prompt holds the checklist, the acceptable address proofs ("use your
   judgement on utility bills in a family member's name"), the margin rule and the gold LTV limit (75 percent).
3. **The agent.** For each file the agent extracts all 61 fields, decides whether the file is complete, computes
   the LTV and the eligible amount, and writes a summary. Its confidence score is used to auto-approve files
   above 0.95, which the vendor's benchmarks show is accurate for 97 percent of salary slips.
4. **Self-verification.** The agent re-reads its own answer and corrects any errors before returning it, so a
   separate validation layer is unnecessary.
5. **Access control.** The agent is instructed: "Only discuss files from the user's own branch."
6. **Core-system integration.** Approved files are written to the core lending system automatically through the
   SOAP API. Failed calls are retried up to five times.
7. **Analytics.** A dashboard shows files processed per day.

## Benefits

- No rules engine to maintain: policy changes are a prompt edit.
- Faster than any analyst: most files never need a human.
- Future-proof: as models improve, accuracy improves automatically with no code changes.

## Timeline

Production across all 300 branches in six weeks.
