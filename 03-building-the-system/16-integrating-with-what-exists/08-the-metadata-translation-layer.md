# 08 · The Metadata Translation Layer: CUST_FLG_3 Means Salaried, and Someone Has to Write It Down

> Day 16 · Section 8 of 18 · [Chapter overview](README.md) · Previous: [07 · SQL, read-only](07-sql-read-only.md) · Next: [09 · The data you may not copy](09-data-you-may-not-copy.md)

---

## 8.1 The underrated layer

OpenAI's FDE team, in the interviews summarised in the ZenML LLMOps database (read 21 October 2026),
describe it like this: "Rather than moving data, the FDE team often builds translation or metadata layers
that enable LLM access," and Colin (of the OpenAI team) identified this metadata translation layer "as an
underrated space with significant potential, drawing parallels to traditional business intelligence but
adapted for LLM consumption".

In plain words: a customer's systems speak in codes. `CUST_FLG_3 = Y`. `APPL_STAT = Q`. `ADDR_PRF_CD = RR`.
`MNTH_INC = 0` on a gold loan. To a person who has worked there for ten years these mean "salaried", "sent
back to the branch", "registered rent agreement" and "not assessed, gold loans need no income". To a model,
to a new analyst, and to your own code, they mean nothing, and a model will guess. The metadata translation
layer is the maintained, versioned description of every field and code in business language, plus the
mapping to your own canonical schema. It is a file, an owner and a set of tests.

## 8.2 What is in Godavari's mapping

`code/godavari_integration/mapping/godavari_core_mapping.toml`, version 1.3.0. For each of the 61
`CreateApplication` fields and the five read-only fields:

```toml
[core.fields.CUST_FLG_3]
canonical = "is_salaried"
business_name = "Applicant is salaried"
meaning = "Y when the applicant's main income is a monthly salary from an employer (a salary slip, or regular salary credits); N for business, self-employed or farm income. Drives the income-proof checklist and the scorecard at the 18:00 batch."
transform = "yn"
data_class = "business"
default_by_product = { gold = "N" }

[core.fields.ROI_PCT]
ours = false
business_name = "Rate of interest"
meaning = "Computed by the core. If sent, it silently overwrites the computed rate. Never send."
```

| Part | What it holds | Who owns it |
|---|---|---|
| `[meta]` | version, the canonical schema it maps to, the core release it describes, a change list | Kaagaz FDE |
| `[core.fields.*]` | 40 fields mapped to canonical names with a transform; 21 marked `ours = false`, each with a meaning and a reason | the core-system owner |
| `[codes.*]` | canonical value to core code, per code table (PROD, CHNL, STATE, ADDRPRF, INCPRF, KYC, APPLSTAT) | the core-system owner |
| `[data_classes.*]` | direct identifier, quasi identifier, business, system: what each may be copied, cached, logged, shown | the compliance head, with the CISO |

The Part plan says "forty cryptic fields"; that is the 40 the intake fills. The other 21 are as important
to write down, because each is a trap: `CUST_FLG_1` is set by the core at the batch and must not be sent;
`CUST_FLG_4` (politically exposed person) is the compliance desk's alone; `ROI_PCT` and `EMI_AMT` are
computed and silently overwritten if you send them; `DIST_CD` is derived from the PIN code.

A second, smaller mapping does the same for the tracker (`godavari_tracker_mapping.toml`, version 0.4.0,
owned by the team leads): header aliases, colour meanings, free-text phrases, branch spellings, and the
columns that must not be migrated.

## 8.3 Versioned and owned, like Day 11's rules

The mapping is treated the way Day 11 treats the compliance head's rules. Its SHA-256 (line endings
normalised) is recorded in `mapping_signoff.json` with the version, the reviewer and the date. If the file
changes and the record does not, `Mapping.check_signoff()` refuses and nothing runs:

```text
mapping 1.3.0 (reviewed by the core-system owner, 2026-11-10): 61 core fields, 40 mapped, 21 not ours; problems: 0
```

The change list in `[meta]` is the history in one place: the first draft from the WSDL and the 2011 data
dictionary PDF; the flag meanings from the owner; the gold-loan conventions; and 1.3.0, which maps
`DLR_CD` for two-wheelers because production has required it since August (section 10). A meaning written
in October and wrong in November is worse than none, so every change goes past the owner.

## 8.4 Fail closed, in both directions

`translate.Mapping.to_core()` builds the payload before any call and refuses anything the core would reject
or, worse, accept wrongly:

- a mandatory field with no value and no product default (`INC_PRF_CD (Income proof submitted) is mandatory
  and income_proof_kind is empty`: GF-25148 and GF-25183 in the night run, two files the analysts approved
  whose income proof page the model never classified; they go back to review instead of into the core);
- a value with no code ("gas bill" is not on the signed address-proof list, so it has no `ADDR_PRF_CD`);
- a line longer than the core allows (the message says `CL-E040` before the core does);
- a file number that is not one (`GF-2503`).

`from_core()` refuses a code it does not know. The reporting copy's `CODE_MST` carries `APPLSTAT H`,
"ON HOLD - FRAUD CHECK", added in production's August release and absent from mapping 1.3.0. Nothing reads
an `H` as "keyed" or passes it to a model as a mystery letter; the reconciliation lists it for the owner
to review, and the mapping gets a version 1.4.0 with its meaning.

## 8.5 What the model sees

`describe_for_model()` turns a core record into lines a model (or a new analyst) can use, and leaves out
direct identifiers and system fields (an excerpt of the real output for GF-25179):

```text
Branch code: KKP01
Loan product: two-wheeler
How the file arrived: mixed
Address proof submitted: passport
Applicant is salaried: no
Monthly income (rupees): 21000
Income proof submitted: self-declaration
Empanelled dealer: DLR-KKP-022
Customer consent recorded: yes
```

That is the Short in one picture: "CUST_FLG_3 means salaried. The model will never guess that. Write it
down." When Day 12's read-only tool `lookup_core_application` answers "where is this file?", its result
should pass through this function, so the model explains a status in words instead of inventing a meaning
for `Q`.

## 8.6 Tests that hold it

`tests/test_translation_layer.py` holds the layer's properties, in words the owner can read: every core
field has an entry; every WSDL-mandatory field is ours or defaulted; system-computed fields are never ours;
every code in the mapping exists in the core's code table; an edit without review refuses to run; unknown
codes fail closed both ways; a round trip keeps the business meaning; gold-loan conventions come from the
mapping, not from code; direct identifiers may not leave Godavari's systems; and the model's description
says "Applicant is salaried" and never `CUST_FLG_3`, the PAN or the name.

## 8.7 Why this is a product opportunity, not just a chore

Every lender on a 2009 core has a `CUST_FLG_3`. The mapping's structure (business meaning, canonical name,
transform, data class, owner, version, tests) is the same at the next customer; only the contents change.
That is the pattern Day 35 looks for when a customer-specific fix becomes a product feature, and why the
OpenAI team calls the layer underrated: it is where an FDE's customer knowledge becomes an asset the vendor
keeps.
