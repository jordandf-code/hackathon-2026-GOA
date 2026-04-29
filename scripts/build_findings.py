"""Synthesize recon/findings.md from the JSON artifacts in recon/raw/.

No DB calls. Pure file I/O so we can iterate without hitting the proxy.
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "recon" / "raw"
OUT = ROOT / "recon" / "findings.md"


def load(name: str):
    return json.loads((RAW / name).read_text())


def fmt_int(n) -> str:
    if n is None:
        return "?"
    return f"{int(n):,}"


def main() -> None:
    version = load("00_version.json")[0]
    schemas = load("01_schemas.json")
    tables = load("02_tables.json")
    exact = {(r["schema"], r["table"]): r["exact_rows"] for r in load("03_exact_counts.json")}
    columns = load("04_columns.json")
    pks = load("05_primary_keys.json")
    fks = load("06_foreign_keys.json")
    indexes = load("07_indexes.json")
    samples = load("08_samples.json")
    dates = load("09_date_minmax.json")
    overlap = load("10_name_overlap.json")

    cols_by_table: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for c in columns:
        cols_by_table[(c["table_schema"], c["table_name"])].append(c)

    pks_by_table: dict[tuple[str, str], list[str]] = defaultdict(list)
    for p in pks:
        pks_by_table[(p["table_schema"], p["table_name"])].append(p["column_name"])

    idx_by_table: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for i in indexes:
        idx_by_table[(i["schemaname"], i["tablename"])].append(i)

    # All "tables" the column catalog knows about (includes views).
    all_objs = sorted({(c["table_schema"], c["table_name"]) for c in columns})
    base_objs = {(t["schema"], t["table"]) for t in tables}
    view_objs = [o for o in all_objs if o not in base_objs]

    # per-schema rollup
    rollup = defaultdict(lambda: {"tables": 0, "rows": 0, "bytes": 0})
    for t in tables:
        s = t["schema"]
        rollup[s]["tables"] += 1
        rollup[s]["rows"] += int(exact.get((s, t["table"])) or 0)
        rollup[s]["bytes"] += int(t["total_bytes"])

    out: list[str] = []
    w = out.append

    w("# Recon: Canadian Federal Spending DB\n")
    w(f"_Source: read-only Render Postgres replica via proxy at `{ROOT.name}`._\n")
    w(f"- Server: `{version['version'].split(' on ')[0]}`")
    w(f"- Database: `{version['db']}`  •  Role: `{version['user']}`")
    w(f"- Raw query outputs: `recon/raw/00..10.json`")
    w("")

    # ---- Verdict up top ----
    w("## Verdict\n")
    w("**(A) Structured fiscal/grants/charity tables, with embedded EN+FR program-purpose text per agreement.**\n")
    w(
        "The dominant content is `fed.grants_contributions` — 1.28M federal grant/contribution "
        "agreements (3 GB), each with a dollar value, recipient, dates, owning department, and "
        "long bilingual prose fields (`prog_name_en/fr`, `prog_purpose_en/fr`, `description_en/fr`, "
        "`expected_results_en/fr`, `agreement_title_en/fr`). That gives us both the $ flows and "
        "the policy-language to classify them against stated commitments. Federal procurement "
        "(`public.contracts`, 153K rows) and Alberta provincial spending (`ab.ab_grants`, 1.99M "
        "rows; `ab.ab_contracts`, `ab.ab_sole_source`) are second-tier sources. CRA charity "
        "schema (49 tables) profiles ~84K registered charities including a per-charity "
        "federal/provincial/municipal funding split. A `general` schema provides an entity-"
        "resolution layer (entities, golden records, splink predictions) that already cross-"
        "links recipients across the fed/cra/ab silos."
    )
    w("")
    w("Not a document corpus, not a knowledge graph — it's a fiscal warehouse with text-rich rows.\n")

    # ---- Schemas ----
    w("## Schemas\n")
    w("| schema | tables | rows | size |")
    w("|---|---:|---:|---:|")
    for s, v in sorted(rollup.items(), key=lambda kv: -kv[1]["bytes"]):
        w(f"| `{s}` | {v['tables']} | {fmt_int(v['rows'])} | {v['bytes']/1e9:.2f} GB |")
    w("")
    w("Schema purpose at a glance:")
    w("- **`fed`** — federal proactive disclosure of grants and contributions (`grants_contributions`) plus lookups; the headline dataset for federal policy-alignment work.")
    w("- **`public`** — federal procurement contracts (`contracts`) with vendor, commodity, indigenous-business flag, and bilingual descriptions.")
    w("- **`cra`** — Canada Revenue Agency charity sector (T3010 returns, identification, financials, directors, government funding by charity, network analyses: `loops`, `johnson_cycles`, `scc_components`).")
    w("- **`ab`** — Alberta provincial grants, contracts, sole-source, and non-profit registry.")
    w("- **`general`** — cross-source entity-resolution layer (entities, golden records, source links, merge candidates, Splink predictions) plus an Alberta-only ministerial history table.")
    w("")

    # ---- Tables ----
    w("## Tables (largest first)\n")
    w("Row counts are exact `count(*)` (NULL = count timed out or view); sizes are `pg_total_relation_size`.\n")
    w("| schema.table | exact rows | est rows | total size |")
    w("|---|---:|---:|---:|")
    for t in tables:
        s, n = t["schema"], t["table"]
        w(f"| `{s}.{n}` | {fmt_int(exact.get((s, n)))} | {fmt_int(t['est_rows'])} | {t['total_size']} |")
    w("")
    if view_objs:
        w("### Views (no on-disk size; reflect underlying tables)")
        for s, n in view_objs:
            w(f"- `{s}.{n}` ({len(cols_by_table[(s, n)])} cols)")
        w("")

    # ---- Per-table columns ----
    w("## Columns by table\n")
    w(
        "Compact format: `name : udt_name [NN]` (NN = NOT NULL). Primary-key columns are "
        "marked with **bold**. Full catalog with precision/scale: `recon/raw/04_columns.json`.\n"
    )
    schemas_order = ["fed", "public", "ab", "cra", "general"]
    seen_schemas = {s for s, _ in all_objs}
    for s in schemas_order + [x for x in seen_schemas if x not in schemas_order]:
        objs_in_schema = sorted([o for o in all_objs if o[0] == s])
        if not objs_in_schema:
            continue
        w(f"### `{s}`\n")
        for sch, tbl in objs_in_schema:
            cols_here = cols_by_table[(sch, tbl)]
            pk_cols = set(pks_by_table[(sch, tbl)])
            kind_marker = "" if (sch, tbl) in base_objs else " *(view)*"
            w(f"#### `{sch}.{tbl}`{kind_marker}")
            w("")
            for c in cols_here:
                name = c["column_name"]
                udt = c["udt_name"]
                nn = " NN" if c["is_nullable"] == "NO" else ""
                if name in pk_cols:
                    w(f"- **`{name}`** : `{udt}`{nn}")
                else:
                    w(f"- `{name}` : `{udt}`{nn}")
            w("")

    # ---- Samples ----
    w("## Samples (3 rows per table, strings truncated to ~200 chars)\n")
    w("Full payloads in `recon/raw/08_samples.json`. Inline below for the policy-relevant headline tables; everything else is in the JSON.\n")
    headline = [
        "fed.grants_contributions",
        "public.contracts",
        "ab.ab_grants",
        "ab.ab_contracts",
        "ab.ab_sole_source",
        "cra.cra_identification",
        "cra.govt_funding_by_charity",
        "cra.govt_funding_by_year",
        "general.entities",
        "general.ministries",
        "general.ministries_history",
        "general.entity_source_links",
    ]
    for key in headline:
        rows = samples.get(key)
        if not isinstance(rows, list) or not rows:
            continue
        w(f"### `{key}` — first row\n")
        w("| column | value |")
        w("|---|---|")
        for k, v in rows[0].items():
            sval = "" if v is None else str(v)
            sval = sval.replace("|", "\\|").replace("\n", " ")
            if len(sval) > 240:
                sval = sval[:240] + "…"
            w(f"| `{k}` | {sval} |")
        w("")

    # ---- Dates ----
    w("## Date / timestamp ranges\n")
    w("Some queries hit the proxy's 30s `statement_timeout` on unindexed scans of the largest "
      "tables — those are listed at the end as `(timeout)`. Full output: `recon/raw/09_date_minmax.json`.\n")
    w("| table.column | type | min | max | non-null |")
    w("|---|---|---|---|---:|")
    timeouts: list[str] = []
    for d in dates:
        full = f"{d['schema']}.{d['table']}.{d['column']}"
        if "error" in d:
            timeouts.append(full)
            continue
        w(f"| `{full}` | `{d['type']}` | {d['min']} | {d['max']} | {fmt_int(d['non_null'])} |")
    if timeouts:
        w("")
        w("**Timed out (need indexes or sampled scan to profile):**")
        for t in timeouts:
            w(f"- `{t}`")
        w("")

    # ---- Join keys ----
    w("## Likely join keys\n")
    w("### Declared foreign keys")
    if fks:
        for fk in fks:
            w(
                f"- `{fk['schema']}.{fk['table']}.{fk['column']}` → "
                f"`{fk['ref_schema']}.{fk['ref_table']}.{fk['ref_column']}`"
            )
    else:
        w("_(none)_")
    w("")
    w(
        "All declared FKs live inside `cra` (loop graph) and `general` (entity resolution). "
        "Cross-schema joins are by convention; the keys to know are below.\n"
    )

    w("### Candidate cross-schema join keys (column-name overlap, manually curated)")
    curated = [
        ("Business Number (CRA charity registration #)",
         ["`fed.grants_contributions.recipient_business_number`",
          "`cra.cra_identification.bn` and every other `cra.*` table",
          "`general.entity_source_links.source_pk` (JSON, includes `bn_root`)"],
         "Bridges federal grants → CRA charity profile and financials. Not a strict FK; "
         "fed `recipient_business_number` includes account suffixes (e.g. `…RP0001`), CRA "
         "uses `bn` (15-char) and `bn_root` (9-char). Strip last 6 chars to align."),
        ("Recipient name (free-text)",
         ["`fed.grants_contributions.recipient_legal_name` / `recipient_operating_name`",
          "`cra.cra_identification.legal_name` / `account_name`",
          "`ab.ab_grants_recipients.recipient`",
          "`general.entities.canonical_name` / `alternate_names`"],
         "Use `general.entities` + `general.entity_source_links` for resolution rather than "
         "string-matching directly; the entity layer already maps source rows to canonical IDs."),
        ("Owning department (federal)",
         ["`fed.grants_contributions.owner_org` / `owner_org_title`",
          "`public.contracts.owner_org` / `owner_org_title`"],
         "Department slug (e.g. `esdc-edsc`) for grouping spending by ministry."),
        ("Province",
         ["`fed.grants_contributions.recipient_province`",
          "`fed.province_lookup`",
          "`cra.cra_province_state_lookup`",
          "`ab.ab_sole_source.department_province` / `vendor_province`"],
         "Two-letter codes; lookup tables in `fed` and `cra`."),
        ("Fiscal period",
         ["`cra.*.fpe` (fiscal_period_end, date)",
          "`cra.cra_financial_general.fiscal_year` (int)",
          "`fed.grants_contributions.agreement_start_date` / `agreement_end_date`",
          "`ab.ab_grants.fiscal_year` / `payment_date`"],
         "CRA uses fiscal-period-end dates; fed uses agreement start/end; AB uses Apr–Mar fiscal year strings."),
        ("Entity ID (cross-source canonical)",
         ["`general.entities.id`",
          "`general.entity_source_links.entity_id` + `(source_schema, source_table, source_pk)`",
          "`general.entity_golden_records.entity_id`",
          "`general.entity_merge_candidates.entity_id_a/b`",
          "`general.entity_resolution_log.entity_id`"],
         "The pre-built bridge from {fed, cra, ab} source rows to a canonical entity. ~927K entities, ~5.16M source links."),
        ("Ministry (Alberta)",
         ["`ab.ab_grants.ministry` / `ab.ab_contracts.ministry` / `ab.ab_sole_source.ministry`",
          "`general.ministries.short_name` / `name`",
          "`general.ministries_crosswalk.raw_ministry` → `canonical_short_name`",
          "`general.ministries_history.short_name`"],
         "`ministries_crosswalk` is the alias-to-canonical bridge for messy raw ministry strings."),
    ]
    for title, keys, note in curated:
        w(f"#### {title}")
        for k in keys:
            w(f"- {k}")
        w("")
        w(note)
        w("")

    w("### Other column-name overlaps")
    w("Full list (any column name that appears in ≥2 tables): `recon/raw/10_name_overlap.json`.\n")

    # ---- Indexes ----
    w("## Indexes (highlights)\n")
    w(f"Total indexes catalogued: {len(indexes)} — full list in `recon/raw/07_indexes.json`.\n")
    w("Notable indexes on the headline tables:\n")
    headline_tables = [
        ("fed", "grants_contributions"),
        ("public", "contracts"),
        ("ab", "ab_grants"),
        ("cra", "cra_identification"),
        ("cra", "cra_financial_general"),
        ("cra", "govt_funding_by_charity"),
        ("general", "entities"),
        ("general", "entity_source_links"),
    ]
    for sch, tbl in headline_tables:
        idxs = idx_by_table.get((sch, tbl), [])
        if not idxs:
            continue
        w(f"**`{sch}.{tbl}`** ({len(idxs)} indexes)")
        for i in idxs[:8]:
            w(f"- `{i['indexname']}` — `{i['indexdef']}`")
        if len(idxs) > 8:
            w(f"- _…and {len(idxs) - 8} more_")
        w("")

    # ---- Open items ----
    w("## Open items / caveats\n")
    w("- **Date min/max timeouts.** Several columns on the largest tables timed out at 30s; rerun with index-aware queries or sampled scans if needed: `agreement_start_date` and `amendment_date` were captured for `fed.grants_contributions` but `vw_grants_decoded` and a few `general` audit-timestamp columns timed out.")
    w("- **Sentinel/garbage dates.** `fed.grants_contributions.agreement_start_date` min is `1899-12-30` (Excel epoch sentinel) and `agreement_end_date` ranges `0209-10-16` → `9999-12-31` — the data needs a `[2010-01-01, today + 5y]` filter for any time-series.")
    w("- **`general.ministries*` is Alberta-only.** Source citation in `ministries_history` is the Wikipedia list of Alberta provincial ministers. There's no federal-ministers table — derive federal departments from `owner_org_title` strings if needed.")
    w("- **Foreign keys are sparse.** Only 11 declared FKs; cross-schema joins must rely on `general.entity_source_links` for canonical entity IDs and on business-number normalization for charity matches.")
    w("- **Text-stats step (artifact 11) was killed mid-run.** Average/max length per text column was deferred to keep the recon scoped. Headline EN-text columns we need to read for policy classification are obvious from samples: `prog_purpose_en`, `description_en`, `expected_results_en`, `agreement_title_en`, `additional_information_en` in `fed.grants_contributions`; `description_en`, `comments_en` in `public.contracts`.")
    w("- **CRA T3010 forms use opaque `field_NNNN` columns.** `cra_financial_details` and `cra_financial_general` are wide tables with hundreds of T3010 line-item codes. We'll need a CRA T3010 codebook to interpret specific lines.")
    w("")

    OUT.write_text("\n".join(out))
    print(f"wrote {OUT.relative_to(ROOT)}: {OUT.stat().st_size:,} bytes, {len(out)} lines")


if __name__ == "__main__":
    main()
