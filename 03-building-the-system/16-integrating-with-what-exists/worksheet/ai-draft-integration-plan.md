# AI-drafted integration plan for Godavari (exercise 3.2: find what is wrong)

> Produced by a coding agent from the prompt "write the integration plan for connecting our intake pipeline to Godavari's core system, SFTP and Excel tracker". It reads well. It contains at least fourteen problems: facts that contradict the discovery pack, decisions that belong to someone else, and engineering that would duplicate loans or leak data. Find them and cite the finding, transcript or owner's sentence each one breaks. Section 15, exercise 3.2.

## Summary

We will integrate Kaagaz's intake pipeline with Godavari's legacy systems in two weeks, starting week 5, once extraction accuracy is final. The plan modernises the 2009 core's interface and removes the analysts' dependence on Excel.

## 1. Core lending system

- Generate a client from the live WSDL at `http://corelend-dev01:7001/...?wsdl` at application start-up, so we always have the latest contract.
- Call `CreateApplication` with retries (three attempts, exponential backoff) to handle the intermittent timeouts the owner mentioned. SOAP is idempotent by design, so retries are safe.
- Validate against the sandbox, which mirrors production.
- To improve throughput at month end, run 20 parallel workers; the core has no documented rate limit.
- Writes can run at any time; the core is a transactional system.
- Map only the 23 mandatory fields; optional fields are optional.
- Set `ROI_PCT` from our pricing model so analysts do not have to.

## 2. Reporting database

- Request a read-write account on the reporting replica so the pipeline can write extraction results next to the core's data for the ops report.
- For speed, the pipeline will check for an existing application in the reporting replica before creating one, instead of calling the slow SOAP lookup.
- Copy `APPL_MST` nightly into Kaagaz's cloud data store so the model can answer questions about any loan.

## 3. SFTP batch

- Poll the region folder every five minutes and process every PDF found. Delete files after processing to avoid reprocessing.
- If a file appears twice, create a new application for the second one, since it may be a different customer.

## 4. Excel tracker

- Analysts will stop using the tracker from day one of the pilot; the review queue replaces it.
- Where we need the tracker's data, read it with pandas (`read_excel`) and map columns by position.
- Colour coding is cosmetic and will be ignored.

## 5. Metadata

- The model will infer the meaning of cryptic fields such as `CUST_FLG_3` from their values; no manual mapping is needed.
- Field descriptions will live in the prompt.

## 6. Data protection

- PII will be encrypted in transit; that satisfies "no PII leaves India".
- Logs will include full request and response payloads for debugging.

## 7. Sign-off

- The CISO approves writes to production.
- Reconciliation is not needed if the client has retries.
