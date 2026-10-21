# Discovery Report: AI-Powered Loan Processing Transformation for Godavari Finance

> Prepared by Kaagaz AI · Version: Final · An AI-written draft for exercise 3.1. It looks finished. It has at least fourteen problems, five kinds of which the checker catches.

## Executive summary

Godavari Finance's loan operations are slow and manual. By deploying a GPT-4o extraction pipeline with RAG over a vector store of loan documents, Kaagaz will make loan processing 67 percent faster, save 12,000 analyst hours a year and deliver 2.4 crore in annual savings. Clean files will be auto-approved, so analysts can focus on exceptions. A branch policy chatbot will follow as a quick win in phase 2, reusing the same vector store.

## 1. Problem statement

> Loan processing at Godavari takes nine days, which is far above the industry benchmark of two days. Manual work and poor document quality are the root causes.

## 2. Stakeholders

| Stakeholder | Role | Interest |
|---|---|---|
| COO | sponsor | faster turnaround |
| Credit-ops analysts | end users | less manual work |
| IT | technical | integration |

## 3. Current workflow

The documented 12-step SOP: the branch uploads the application, credit-ops keys it into the core system, checks the documents against the checklist, runs the credit check and sanctions. Our solution automates steps 2 to 4.

## 4. Key findings

- Documents are mostly scanned PDFs; modern OCR and LLMs handle these well.
- Historical loan decisions (50,000 labelled files) are available to fine-tune the model.
- The core system exposes a SOAP API that can be wrapped in a REST layer.

## 5. Solution and workstreams

| Workstream | Weeks |
|---|---|
| RAG pipeline and vector store | 1 to 4 |
| Fine-tuning on historical files | 3 to 6 |
| Review UI | 5 to 8 |
| Integration | 9 |
| Security review | 8 to 10 |

## 6. The 90-day plan

All 300 branches go live in week 8, with auto-approval for files scoring above 0.9 confidence. See [the 90-day plan](../../08-scoping-the-first-90-days/worksheet/90-day-plan.md).

## 7. Baseline and business case

Turnaround is nine days today (industry benchmark: two). The system targets 2 days and 100 percent accuracy on KYC fields, saving 2.4 crore a year in analyst cost. Details in [the discovery synthesis](../../06-discovery-interviews/worksheet/discovery-synthesis.md).

## 8. Data and security

All data is processed in a secure, SOC 2 compliant cloud region with encryption at rest and in transit. Godavari's files improve the model over time through continuous fine-tuning.

## 9. Risks

| Risk | Mitigation |
|---|---|
| hallucination | RAG grounding |
| user adoption | training sessions |

## 10. Out of scope

| Item | Reason |
|---|---|
| Branch CRM | deferred |
| Collections summaries | phase 2 |
| Core system changes | |

## 11. Decisions needed

| Decision | Owner | Date |
|---|---|---|
| approve the GPT-4o pipeline | TBD | |
| approve auto-approval threshold | Godavari leadership | ASAP |
| approve phase 2 chatbot | COO | |

## Decision log

| Decision | Decided by | Date |
|---|---|---|
| use RAG architecture | Kaagaz | week 1 |

## Sign-off

Approved by Godavari leadership.
