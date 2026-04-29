# Reference data

Hand-curated lookup files used by the policy-alignment demo. Not authoritative
— always cross-check against the CRA forms before publishing analysis.

## `t3010_minimal.csv`

Minimal codebook for the `field_NNNN` columns on `cra.cra_financial_general`
and `cra.cra_financial_details`. **Covers ~30 lines, not the full ~300+ on the
T3010** — only the lines we expect to touch in the demo (government revenue
splits, key expenditure functional categories, foreign-activity spend,
advocacy spend, grand totals).

### Columns
| column | meaning |
|---|---|
| `field_code` | the column name as it appears in the schema (e.g. `field_4540`) |
| `table` / `column` | where it lives in the warehouse |
| `label_en` | short English label for the line |
| `category` | `flag` / `revenue` / `expense` / `subtotal_rev` / `subtotal_exp` |
| `policy_relevance` | one-line note on why we'd query it for the demo |
| `confidence` | `high` (well-known T3010 line, label stable across years) / `medium` (general meaning correct, exact wording varies by year) |
| `notes` | sourcing or pitfalls |

### Provenance
Labels are reconstructed from the structure of the T3010 *Registered Charity
Information Return* and Guide T4033, *Completing the Registered Charity
Information Return* (Canada Revenue Agency). They are **not** copied from a
single canonical CRA dictionary file — entries marked `medium` confidence
should be verified against the current T3010 PDF before quoting in any
public-facing output.

### How to extend
1. Pull the current T3010 from the CRA forms catalogue.
2. For each line you need to interpret, add a row to `t3010_minimal.csv` with
   the exact label from the form.
3. If we end up needing the full ~300-line dictionary, replace this file with
   the data dictionary published alongside the T3010 dataset on
   `open.canada.ca` (load it as a regular CSV — no DB write required since the
   warehouse is read-only).

### Caveats baked in
- `cra.cra_financial_general` and `cra.cra_financial_details` *both* contain
  some of the same numbered fields (e.g. `field_5000`, `field_5010`,
  `field_5030`). In `cra_financial_general` they tend to be activity
  flags / indicators; in `cra_financial_details` they are the dollar amounts
  from Schedule 6. Always pick the table appropriate to your question — this
  codebook lists the table we expect to query for each line.
- CRA renamed "political activities" to "public policy dialogue and
  development activities" around 2019; the column number (`5030`) and flag
  (`1800`) stayed the same.
- Schedule 6 line numbers have been stable across recent T3010 revisions, but
  some subtotal lines (e.g. `4650` vs `4700`, `5050` vs `5100`) have shifted
  meaning across form versions. When in doubt, prefer the unambiguous grand
  totals: `field_4700` for total revenue, `field_5900` for total expenditures.
