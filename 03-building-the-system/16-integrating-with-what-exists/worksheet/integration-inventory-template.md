# Integration inventory · template for the next customer

> Day 16 worksheet. One row per system the AI system reads from or writes to. Fill it in the first two weeks, with the system's owner in the room, before any client code is written. Every empty cell is a risk; write "unknown" rather than leave it blank, and put the question in section 3.

## 1. The systems

| System | Protocol and contract (WSDL, schema, file layout) | Direction (read, write) | Owner (a person) | Who grants access | Freshness | Windows (batch, freeze, maintenance) | Rate limit (documented? measured?) | Idempotency (key? lookup? natural key?) | Sandbox (exists? refreshed when? what differs?) | May we copy the data? | Contract test | Reconciliation |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| | | | | | | | | | | | | |

## 2. For every write

| Operation | Natural key | Where our key is stamped | What a timeout means (did it commit?) | The system's transaction ceiling | Quiet period before a lookup decides | Who resolves a duplicate |
|---|---|---|---|---|---|---|
| | | | | | | |

## 3. Questions for the owner

| # | Question | Why it matters | Answer | Date |
|---|---|---|---|---|
| 1 | What happens if we call create twice for the same record? | duplicates on retry | | |
| 2 | Is there an operation that finds a record by our natural key? | lookup before create | | |
| 3 | When is nothing allowed to write? | the window | | |
| 4 | How many calls a second will it take? Has anyone measured? | the limit nobody wrote down | | |
| 5 | How old is the sandbox, and what changed in production since? | stale contract tests | | |
| 6 | Which fields does the system compute itself? | sending them overwrites them | | |
| 7 | Which spare field can carry our reference? | telling our records from keyed ones | | |
| 8 | Which tables and columns may we read, and which never? | the read-only sign-off | | |
| 9 | What would you need to see before you let us write to production? | the condition, in his words | | |
| 10 | Who on your side owns this after we leave? | handoff (Day 28) | | |

## 4. The metadata translation layer

| Source field or code | Business meaning (in the owner's words) | Canonical field | Transform | Data class | Owner | Version |
|---|---|---|---|---|---|---|
| | | | | | | |
