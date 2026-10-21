# Godavari discovery findings (AI draft, for exercise 3.1 in section 15)

> A colleague pasted the ten transcripts into a chat assistant and asked it to "write the discovery findings for the readout". This is what came back, lightly formatted. It reads well. At least eight of its findings are not supported by anything an interviewee said, and the tally script catches the ones that carry a code. Do not use it; review it.

## Key findings

**1. Analysts are enthusiastic about AI assistance and would welcome a conversational assistant for policy questions.** [CHATBOT_WANTED]
Across the interviews, analysts repeatedly expressed frustration with looking up policy and would benefit from a chatbot over the circulars.

**2. Branch visibility is enforced by Active Directory groups.** [BRANCH_ISOLATION] [ACCESS_VIA_AD_GROUPS]
The CISO and others confirmed that users only see their own branch's files. This can be handled at index time by tagging documents with the branch.

**3. The core system exposes a REST API that the solution can call in real time.** [REST_API_AVAILABLE]
Integration is straightforward via the core's modern API layer, with real-time status updates.

**4. A credit bureau API is available for real-time credit checks.** [BUREAU_API_REALTIME]
This removes the dependency on the overnight batch.

**5. Analysts spend most of their time on data entry.** [REKEYING]
The 61-field form is the main bottleneck; automating it will deliver most of the nine-to-three improvement.

**6. The Excel tracker is a legacy workaround that can be retired in phase one.** [SHADOW_TRACKER]
Once the system is live, the tracker becomes redundant and analysts indicated they would be happy to stop using it.

**7. Current field-level accuracy of manual entry is approximately 92 percent.** [MANUAL_ACCURACY_92]
This provides the baseline the model must beat.

**8. The compliance head is open to the model determining document acceptability using learned patterns.** [RULES_AS_SIGNED_CODE]
She indicated flexibility on how completeness is assessed as long as audit outcomes are maintained.

**9. Files arrive via WhatsApp and should be ingested through a WhatsApp Business integration.** [WHATSAPP_CHANNEL] [WHATSAPP_INGEST]
This captures the 20 percent of pages currently lost.

**10. Data can be processed in the vendor's cloud with appropriate encryption.** [ENCRYPTED_OFFSHORE_OK]
The CISO's concerns are addressed by encryption at rest and in transit.

**11. The sanction decision could be automated for low-risk files to maximise turnaround gains.** [AUTO_SANCTION_LOW_RISK]
The COO is primarily focused on speed.

**12. Month end is a busy period.** [BAD_DAY_MONTH_END]
Load is higher in the last days of the month.

## Recommendation

Deploy an LLM-powered document pipeline with RAG over the policy circulars, WhatsApp ingestion, real-time core integration and auto-sanction for clean files, across all 300 branches in phase one.
