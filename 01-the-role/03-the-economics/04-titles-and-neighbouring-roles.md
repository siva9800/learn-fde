# 04 · Titles and Neighbouring Roles: Who Pays, When, and What Is Measured

> Day 3 · Section 4 of 12 · [Chapter overview](README.md) · Previous: [03 · The services trap](03-the-services-trap.md) · Next: [05 · Pay: US and India](05-pay-us-and-india.md)

---

## 4.1 Four roles that get confused with each other

[Day 2](../02-the-three-buckets/README.md) separated the roles by what the week looks like. This
section separates them by money: who pays for the role, at what point in the customer's life, and
what number the person is judged on. The economics are what make the titles different, and they
are also what make the pay different (section 05).

| | Forward deployed engineer | Solutions engineer (pre-sales) | Consultant or systems integrator | Applied AI engineer | Customer engineer (post-deployment) |
|---|---|---|---|---|---|
| Who pays for the role | The vendor, out of product margin, to secure recurring revenue | The vendor, out of sales budget | The client, by the hour or by the build | The vendor, out of engineering or product | The vendor, out of support or success budget |
| When in the customer's life | After the deal, for weeks or months, until the customer is self-sufficient | Before the deal; winds down after close | Whenever a statement of work is signed; ends when it ends | Often not customer-specific; builds the product's AI features, sometimes embedded like an FDE | After deployment, ongoing |
| Where the spec comes from | The customer's problem, inside the vendor's product | The sales opportunity: the demo that wins | The client's requirements document | The product roadmap, informed by customers | Escalations and usage |
| What is measured | Recurring revenue per engineer; the renewal; patterns shipped to product; the customer running it without you | Revenue influenced; deals closed | Billable utilisation; delivery against the SOW | Eval scores, feature delivery, model quality | Retention, escalation resolution, usage |
| Pay structure (recruiter-reported, 2026) | Salary plus equity, equity often half or more at senior levels | Base plus variable tied to deals (OTE) | Salary; bonus on utilisation or project margin | Salary plus equity | Base plus bonus |
| Owns the outcome? | Yes: if the deployment fails, the FDE is accountable | No: the deal is the finish line | Contractually the firm, not the engineer | Partly: the feature, not the customer's outcome | For keeping it running, not for the first deployment |

The sources behind the table: Paraform's April 2026 comparison of FDE, solutions engineer and
customer engineer (a recruiting firm; its pay figures are its own estimates), the 2026 analysis of
1,000 postings (June 2026), and fde.directory's July 2026 note on India, whose advice for reading
a posting is the same as this table's bottom row: read the job description for who is accountable
when the deployment fails, because that question sorts most of the pay spread.

Two things the table makes visible that the Day 2 week-shape did not:

- **The FDE is paid from product margin.** That is why the ratio in section 02 exists: a role paid
  from margin has to be justified by the margin it protects. A solutions engineer is justified by
  the deals; a consultant by the invoice.
- **Applied AI engineer is the same job with the weight moved.** Anthropic's postings for "Forward
  Deployed Engineer, Applied AI" use both words in one title; the 1,000-posting analysis lists
  Applied AI Engineer as one of the six variants. When the posting says the engineer sits with
  customers and owns a deployment, it is an FDE role with more evals in it. When it says the
  engineer builds the product's AI features and talks to customers occasionally, it is a product
  role. The pay follows the customer-outcome share, not the title.

## 4.2 The six title variants

The June 2026 analysis of 1,000 FDE job postings found the role advertised under six titles, and
estimated that about a third of the live market sits under the adjacent ones:

| Title | What it usually means | Watch for |
|---|---|---|
| Forward Deployed Engineer | The role as this course defines it | Whether it is billed to a client |
| Forward Deployed AI Engineer | The same, with the applied-AI bucket emphasised | Sometimes a prompt-engineering role with travel |
| Applied AI Engineer | Product-side or FDE-side, see above | Which side the outcome ownership sits |
| Deployment Engineer or Solutions Engineer | Post-sale implementation, often narrower scope | Whether it is configuration only, with no code |
| Forward Deployed Software Engineer (FDSE) | Palantir's title; others copy it | At non-Palantir companies, usually the same as FDE |
| FDE / Solutions Architect (hybrid) | Design plus deployment, often at larger vendors and GCCs | Whether "architect" means you do not write code |

Practical consequence: search all six. A search for the exact phrase "forward deployed engineer"
misses a third of the roles, and some of the best-paid ones (Anthropic's applied-AI postings, the
GCC hybrid roles) are under the other names.

## 4.3 The posting that is a consulting job wearing the title

Because the title is fashionable, it is being used for roles that have none of the economics. The
signs, from the three sources above and from the Part 1 plan:

| In the posting | What it tells you |
|---|---|
| "billed to client", "statement of work", "client engagement model", "utilisation" | The client pays by the hour. This is consulting. |
| "work across multiple client accounts delivering custom solutions" with no product named | There is no product to send patterns to; every build is from zero |
| The company is a services firm and the role sits in a "practice" | The economics are the practice's, whatever the title |
| No mention of what the engineer owns after go-live | Nobody is accountable for the outcome; probably a staffing role |
| "travel up to 50 percent" plus "implementation tickets" | A deployment engineer; fine, but priced as one |
| "customer outcomes", "renewal", "expansion", "patterns to product", "own the deployment end to end" | The FDE economics are present; the 1,000-posting analysis found these postings pay more |

The source's phrase is the one to remember: **the scope language matters more than the title.**

None of this makes a services role a bad job. The Indian IT majors and the consulting firms are
training a large share of the engineers who will hold FDE titles in 2028, and a services role at a
firm that deploys AI into real companies teaches bucket one and bucket three well. The point is to
know what you are accepting, and to price it correctly (section 06).

## 4.4 Key takeaways

- The roles differ by who pays, when, and what is measured. The FDE is paid from product margin,
  after the deal, on recurring revenue and the renewal, and owns the outcome.
- Six title variants; about a third of the market under the adjacent ones; search all six.
- The scope language matters more than the title. "Billed to client" and "utilisation" mean
  consulting; "owns the deployment", "renewal" and "patterns" mean FDE.
