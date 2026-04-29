# Policy-alignment agent — design

A PBO-style independent oversight agent. Given a stated federal commitment
(from `data/commitments.yaml`), it answers two questions:

1. **What did the government say it would do?** — pledge amount, window,
   target date, departments, source.
2. **What actually happened?** — sum of grants/contributions and contracts
   that match the commitment, broken down by year, department, and recipient,
   with deep-links into the source rows. Surface the gap.

The v1 demo is reconciliation-only. The system is theme-agnostic; adding
emissions / housing / healthcare is a matter of extending `commitments.yaml`.

## Why this is "agentic" and not just SQL

The agent autonomously decides:

- which queries to run for a commitment (keyword-based filter? department
  filter? recipient_type filter? all three? plus contracts?),
- when to widen / narrow keywords based on initial result counts,
- when an agreement matches the commitment (LLM judgment on
  `prog_purpose_en` + `agreement_title_en` rather than substring match),
- how to summarize the gap (narrative + numbers + citations).

It runs a tool-use loop with read-only access to the warehouse via the proxy.

## Module layout

```
agent/
├── README.md                  this file
├── __init__.py
├── db.py                      thin wrapper around the proxy /query endpoint
├── commitments.py             load + lookup data/commitments.yaml
├── classifier.py              LLM-backed scorer: agreement → commitment fit
├── tools.py                   tool schemas exposed to the model
├── orchestrator.py            tool-use loop (anthropic SDK, with caching)
└── cli.py                     entry point: python -m agent.cli <commitment-id>
```

## Tools exposed to the model

Each tool is small, returns JSON, and is read-only.

| name | input | output | notes |
|---|---|---|---|
| `commitments_list` | `theme?` | `[{id, title, pledge_amount_cad, target_date}]` | Pre-loaded from YAML; no DB hit. |
| `commitment_get` | `id` | full commitment record | YAML lookup. |
| `db_sql` | `sql` | `{columns, rows, row_count, truncated}` | Forwards to proxy `/query`. Hard-capped by proxy at SELECT/WITH/SHOW/EXPLAIN, 10k rows, 30s. |
| `db_describe` | `table` | columns + a sample row | Convenience; saves the model from repeating `information_schema` queries. |
| `agreements_match_commitment` | `commitment_id`, `year`, optional `limit` | sample of fed.grants_contributions rows pre-filtered by department/keyword/recipient_type, with a per-row LLM fit score 0-1 | The classifier is what makes the system robust to keyword drift. Cached per (commitment_id, year). |
| `contracts_match_commitment` | `commitment_id`, `year` | same idea against public.contracts | Drives the procurement-target story. |
| `aggregate_spend` | `commitment_id`, optional `year_range` | totals + by-year + by-department breakdown | Calls `agreements_match_commitment` under the hood; returns aggregated dollars and a recipient leaderboard. |

The model is allowed to compose these freely. For the demo, the orchestrator
seeds it with the commitment id and a single instruction; the model decides
the rest.

## Demo flow (5 minutes)

1. **0:00 — frame.** "We're a PBO-style auditor. Given a stated federal
   commitment, can we independently verify what the data shows?"
2. **0:30 — pick a commitment.** `python -m agent.cli mmiwg-national-action-plan`
   (or `indigenous-procurement-target-5pct` for the cleanest beat).
3. **0:45 — agent runs live.** Streams its tool calls to the terminal so
   judges see real autonomous reasoning. Calls hit the live warehouse via the
   proxy.
4. **2:30 — verdict.** Agent prints:
   - pledge: $2.2B over 5y across 4 departments
   - actual flows tagged to MMIWG response by year (table)
   - top 10 recipients with deep-links
   - gap statement with caveats
5. **3:30 — second commitment, same pipeline.** Run
   `indigenous-procurement-target-5pct` to show generality. This one is the
   strongest single beat because it's directly testable against
   `public.contracts.indigenous_business`.
6. **4:30 — close.** "Same pipeline. Add a `commitments.yaml` entry, get an
   audit. Show one slide of an emissions-themed commitment running through
   the same agent."

## Implementation choices to lock in before coding

- **Model.** Default to `claude-sonnet-4-6` for tool-use loop. The
  classifier (per-agreement fit scoring) batches via prompt caching so cost
  stays low even on commitments with thousands of candidate agreements.
- **Caching.** Use `cache_control` blocks on the system prompt (commitment
  list + schema crib sheet) and on the per-commitment classifier prompt.
- **No state in DB.** All caches go to local JSON in `agent/.cache/`. The
  warehouse is read-only.
- **Determinism in the demo.** Save each tool call's output to
  `agent/.cache/runs/<run-id>/` so the demo is replayable if the network
  flakes or the proxy cold-starts.
- **Department slug validation.** First action on every run: `SELECT DISTINCT
  owner_org FROM fed.grants_contributions ORDER BY 1` and persist to cache.
  Resolve placeholder slugs in `commitments.yaml` against this list.
- **Money formatting.** Always print CAD with the year and a flag for whether
  the figure is cumulative within the pledge window vs the full lifetime.

## Out of scope for v1

- Provincial spending alignment (`ab.*`) — interesting but not needed for the
  PBO-style federal frame.
- CRA charity-side analysis (`cra.*`) — useful as a follow-up ("does federal
  funding flow to charities that report aligned program activities?") but
  adds a layer of resolution that doesn't fit a 5-minute demo.
- French-side text matching. We rely on `*_en` columns; bilingual coverage is
  a v2 feature.
- Splink / entity-resolution joins. The dataset's `general.entity_source_links`
  is rich but using it well is a project on its own; v1 matches recipients by
  business number (`recipient_business_number` ↔ `cra_identification.bn`)
  only when needed.
- Authoring (web UI, dashboard). v1 is a CLI; if there's leftover time after
  the demo works end-to-end, a single Streamlit page renders the same
  output.

## Risks

- **Keyword recall.** Keyword filters miss agreements that don't use our
  vocabulary. Mitigation: run the classifier over a broader candidate set
  (e.g. all agreements with `recipient_type='A'` for Indigenous commitments)
  rather than relying solely on keyword pre-filter.
- **Pledge amount accuracy.** Several entries in `commitments.yaml` are
  marked `medium` confidence. Verify dollar amounts and dates against
  primary sources before the demo or downgrade those entries to qualitative.
- **Agreement-amendment double-counting.** `fed.grants_contributions` has
  `is_amendment` and `amendment_number` fields. Aggregations must dedupe by
  `agreement_number` and use the latest amendment, otherwise totals balloon.
- **Date sentinels.** `agreement_start_date` ranges include `1899-12-30`
  (Excel epoch) and `agreement_end_date` includes `9999-12-31`. The
  `db.sql` tool prompt should remind the model to filter to a sane window.
