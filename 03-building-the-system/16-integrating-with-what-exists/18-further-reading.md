# 18 · Further Reading

> Day 16 · Section 18 of 18 · [Chapter overview](README.md) · Previous: [17 · Exercises](17-exercises.md)

---

Pages marked "read 21 October 2026" were fetched for this chapter on that date. The others are standard
references cited from the Part plan or well known; their URLs were not re-fetched for this chapter.

## The FDE sources behind this chapter

| Resource | Why read it |
|---|---|
| OpenAI forward deployed engineering, ZenML LLMOps database summary: https://www.zenml.io/llmops-database/forward-deployed-engineering-bringing-enterprise-llm-applications-to-production (read 21 October 2026) | "translation or metadata layers that enable LLM access"; the metadata translation layer as "an underrated space"; MCP as "a starting point for data connectivity" with logic layers built on top; the question of whether data needs to move at all |
| The second OpenAI FDE interview summary: https://www.zenml.io/llmops-database/forward-deployed-engineering-for-enterprise-llm-adoption | the same team's view of enterprise adoption across OpenAI, Ramp, Nominal and Dataland |
| Atlassian, Forward Deployed Engineering Playbook: https://www.atlassian.com/blog/guides-research/forward-deployed-engineering-playbook | working inside the customer's systems; the 12-week bar that the handoff (Day 28) inherits |

## SOAP, WSDL and WS-Security

| Resource | Why read it |
|---|---|
| zeep documentation: https://docs.python-zeep.org/ ; transports: https://docs.python-zeep.org/en/master/transport.html ; WS-Security: https://docs.python-zeep.org/en/master/wsse.html (read 21 October 2026) | `timeout` (documents, default 300 s) versus `operation_timeout` (calls); `UsernameToken`; settings such as `strict`. zeep 4.3.3 is the pinned version |
| W3C, Simple Object Access Protocol (SOAP) 1.1, Note, 8 May 2000: https://www.w3.org/TR/2000/NOTE-SOAP-20000508/ | the envelope, the header, the body and the Fault element with `faultcode` and `faultstring` |
| W3C, Web Services Description Language (WSDL) 1.1, Note, 15 March 2001: https://www.w3.org/TR/wsdl | types, messages, portType, binding, service; document versus rpc style |
| OASIS, Web Services Security UsernameToken Profile 1.0: https://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0.pdf | PasswordText versus PasswordDigest; what the core's header carries |

## Idempotency, outboxes and integration patterns

| Resource | Why read it |
|---|---|
| Stripe API reference, Idempotent requests: https://docs.stripe.com/api/idempotent_requests | the server-side idempotency key pattern this chapter has to rebuild on the client side, and why |
| Chris Richardson, Transactional outbox pattern: https://microservices.io/patterns/data/transactional-outbox.html | intent recorded with your own state before delivery; the journal is a small version |
| Gregor Hohpe and Bobby Woolf, Enterprise Integration Patterns: https://www.enterpriseintegrationpatterns.com/ | file transfer, shared database, remote procedure invocation, messaging: the four integration styles, and the idempotent receiver |
| Martin Fowler, Contract Test: https://martinfowler.com/bliki/ContractTest.html | testing the boundary against a recorded or simulated counterpart instead of the live system |
| Pact, consumer-driven contract testing: https://docs.pact.io/ | the fuller version of contracts, when you can influence the provider |

## Files, spreadsheets and databases

| Resource | Why read it |
|---|---|
| paramiko SFTP client: https://docs.paramiko.org/en/stable/api/sftp.html (read 21 October 2026) | `listdir_attr`, `stat`, `open`, `rename` versus `posix_rename`; the pinned version is 4.0.0 |
| openpyxl, read-only mode and its limits: https://openpyxl.readthedocs.io/en/stable/optimized.html (read 21 October 2026) | why the tracker reader uses normal mode (fills, hidden rows, merged cells) and closes workbooks |
| Python `sqlite3`: https://docs.python.org/3/library/sqlite3.html (read 21 October 2026) | read-only URIs (`mode=ro`), `set_authorizer` with `SQLITE_DENY`, `set_progress_handler` |
| SQLite, the authorizer callback: https://www.sqlite.org/c3ref/set_authorizer.html | the action codes and what the callback sees, for the column-level allowlist |
| Debezium documentation: https://debezium.io/documentation/ | change data capture, for exercise 3.4 |
| Model Context Protocol: https://modelcontextprotocol.io/ | exposing tools and resources to model clients; section 12's caveats apply |

## Indian context (owned by Days 23 and 24)

| Resource | Why read it |
|---|---|
| The Digital Personal Data Protection Act, 2023 (India Code): https://www.indiacode.nic.in/handle/123456789/19714 | the law behind "no customer PII leaves India"; Day 24 owns the detail and the rules |
| Reserve Bank of India, Master Direction on KYC, 2016, as amended: https://www.rbi.org.in/Scripts/BS_ViewMasDirections.aspx?id=11566 | why the masked Aadhaar reference is the only Aadhaar the core and the mapping carry |

## Inside this course

- [Day 6](../../02-discovery-and-decomposition/06-discovery-interviews/README.md): transcript 06 and findings A2, A4 and A5, the facts this chapter implements.
- [Day 7](../../02-discovery-and-decomposition/07-decomposition/README.md): the inputs inventory these four systems come from.
- [Day 11](../11-the-system-around-the-model/README.md): the intake package and `push_to_core`, imported by path.
- [Day 12](../12-llm-apis-for-production/README.md): read-only tools that should call this chapter's port, and retries for calls where a repeat only costs money.
- [Day 17](../17-agents-and-workflows/README.md): the state machine and idempotency keys for every workflow step.
- [Day 19](../19-observability-for-ai-systems/README.md): the alerts this chapter names but does not build.
- [Day 23](../../04-deploying-into-their-world/23-security-review-and-procurement/README.md) and [Day 24](../../04-deploying-into-their-world/24-data-residency-and-indian-law/README.md): the contract and the law behind section 09.
- [Day 25](../../04-deploying-into-their-world/25-network-secrets-and-egress/README.md): the network path to the core after the move to Mumbai.
- [Day 28](../../04-deploying-into-their-world/28-handoff-and-self-sufficiency/README.md): handing the integration to Godavari's application-support engineer.
