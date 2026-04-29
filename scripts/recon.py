"""Read-only reconnaissance of the provided Postgres replica via the
deployed HTTPS proxy (proxy/main.py on Render).

Saves raw query outputs to recon/raw/*.json so we can re-read them without
re-querying. Set PROXY_URL + PROXY_TOKEN in .env (see .env.example).
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "recon" / "raw"
RAW.mkdir(parents=True, exist_ok=True)

load_dotenv(ROOT / ".env")
PROXY_URL = os.environ["PROXY_URL"].rstrip("/")
PROXY_TOKEN = os.environ["PROXY_TOKEN"]
SESSION = requests.Session()
SESSION.headers["Authorization"] = f"Bearer {PROXY_TOKEN}"


def q(sql: str, limit: int | None = None) -> tuple[list[str], list[dict[str, Any]]]:
    r = SESSION.post(f"{PROXY_URL}/query", json={"sql": sql, "limit": limit}, timeout=120)
    if r.status_code >= 400:
        raise RuntimeError(f"proxy {r.status_code}: {r.text[:500]}")
    d = r.json()
    if d.get("truncated"):
        print(f"  WARN: result truncated at row_count={d['row_count']}")
    return d["columns"], d["rows"]


def dump(name: str, payload) -> None:
    path = RAW / f"{name}.json"
    path.write_text(json.dumps(payload, indent=2, default=str))
    print(f"  wrote {path.relative_to(ROOT)}")


def truncate(value, limit=200):
    if isinstance(value, str) and len(value) > limit:
        return value[:limit] + f"...[+{len(value) - limit}ch]"
    return value


def main() -> int:
    print("== version + current db ==")
    _, version = q("SELECT version() AS version, current_database() AS db, current_user AS \"user\"")
    dump("00_version", version)
    print(version)

    print("\n== schemas ==")
    _, schemas = q(
        """
        SELECT n.nspname AS schema,
               pg_catalog.pg_get_userbyid(n.nspowner) AS owner
        FROM pg_catalog.pg_namespace n
        WHERE n.nspname NOT IN ('pg_catalog','information_schema')
          AND n.nspname NOT LIKE 'pg_toast%'
          AND n.nspname NOT LIKE 'pg_temp%'
        ORDER BY 1
        """
    )
    dump("01_schemas", schemas)
    for s in schemas:
        print(f"  {s['schema']} (owner={s['owner']})")

    print("\n== tables w/ size + row estimates ==")
    _, tables = q(
        """
        SELECT n.nspname AS schema,
               c.relname AS \"table\",
               c.reltuples::bigint AS est_rows,
               pg_total_relation_size(c.oid) AS total_bytes,
               pg_relation_size(c.oid) AS heap_bytes,
               pg_size_pretty(pg_total_relation_size(c.oid)) AS total_size,
               pg_size_pretty(pg_relation_size(c.oid)) AS heap_size,
               c.relkind
        FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE c.relkind IN ('r','m','p','f')
          AND n.nspname NOT IN ('pg_catalog','information_schema')
          AND n.nspname NOT LIKE 'pg_toast%'
        ORDER BY pg_total_relation_size(c.oid) DESC
        """
    )
    dump("02_tables", tables)
    for t in tables:
        print(f"  {t['schema']}.{t['table']}  est_rows={t['est_rows']:>10}  size={t['total_size']}")

    print("\n== exact row counts ==")
    exact_counts = []
    for t in tables:
        if t["relkind"] not in ("r", "m", "p"):
            continue
        full = f'"{t["schema"]}"."{t["table"]}"'
        try:
            _, rows = q(f"SELECT count(*) AS n FROM {full}")
            n = rows[0]["n"] if rows else None
        except Exception as e:
            n = None
            print(f"  count failed for {full}: {e}")
        exact_counts.append({"schema": t["schema"], "table": t["table"], "exact_rows": n})
        print(f"  {full}: {n}")
    dump("03_exact_counts", exact_counts)

    print("\n== columns ==")
    _, columns = q(
        """
        SELECT table_schema, table_name, ordinal_position, column_name,
               data_type, udt_name, is_nullable, character_maximum_length,
               numeric_precision, numeric_scale
        FROM information_schema.columns
        WHERE table_schema NOT IN ('pg_catalog','information_schema')
        ORDER BY table_schema, table_name, ordinal_position
        """
    )
    dump("04_columns", columns)
    by_table: dict[tuple[str, str], list[dict]] = {}
    for c in columns:
        by_table.setdefault((c["table_schema"], c["table_name"]), []).append(c)
    for (sch, tbl), cols in by_table.items():
        print(f"  {sch}.{tbl}:")
        for c in cols:
            print(f"    {c['column_name']:<30} {c['udt_name']:<20} null={c['is_nullable']}")

    print("\n== primary keys ==")
    _, pks = q(
        """
        SELECT tc.table_schema, tc.table_name, kc.column_name, kc.ordinal_position
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kc
          ON kc.table_schema = tc.table_schema
         AND kc.table_name = tc.table_name
         AND kc.constraint_name = tc.constraint_name
        WHERE tc.constraint_type = 'PRIMARY KEY'
          AND tc.table_schema NOT IN ('pg_catalog','information_schema')
        ORDER BY tc.table_schema, tc.table_name, kc.ordinal_position
        """
    )
    dump("05_primary_keys", pks)

    print("\n== foreign keys ==")
    _, fks = q(
        """
        SELECT tc.table_schema AS schema, tc.table_name AS \"table\",
               kcu.column_name AS \"column\",
               ccu.table_schema AS ref_schema, ccu.table_name AS ref_table,
               ccu.column_name AS ref_column,
               tc.constraint_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
          ON tc.constraint_name = kcu.constraint_name
         AND tc.table_schema = kcu.table_schema
        JOIN information_schema.constraint_column_usage ccu
          ON ccu.constraint_name = tc.constraint_name
         AND ccu.table_schema = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY'
          AND tc.table_schema NOT IN ('pg_catalog','information_schema')
        ORDER BY tc.table_schema, tc.table_name
        """
    )
    dump("06_foreign_keys", fks)
    for fk in fks:
        print(f"  {fk['schema']}.{fk['table']}.{fk['column']} -> {fk['ref_schema']}.{fk['ref_table']}.{fk['ref_column']}")

    print("\n== indexes ==")
    _, indexes = q(
        """
        SELECT schemaname, tablename, indexname, indexdef
        FROM pg_indexes
        WHERE schemaname NOT IN ('pg_catalog','information_schema')
        ORDER BY schemaname, tablename, indexname
        """
    )
    dump("07_indexes", indexes)

    print("\n== samples (3 rows each, truncated) ==")
    samples: dict[str, Any] = {}
    for t in tables:
        if t["relkind"] not in ("r", "m", "p"):
            continue
        full = f'"{t["schema"]}"."{t["table"]}"'
        key = f'{t["schema"]}.{t["table"]}'
        try:
            _, rows = q(f"SELECT * FROM {full} LIMIT 3")
            for r in rows:
                for k, v in list(r.items()):
                    r[k] = truncate(v) if isinstance(v, str) else v
            samples[key] = rows
            print(f"  {key}: {len(rows)} rows")
        except Exception as e:
            samples[key] = {"error": str(e)}
            print(f"  {key}: ERROR {e}")
    dump("08_samples", samples)

    print("\n== date / timestamp min/max ==")
    date_udts = {"date", "timestamp", "timestamptz"}
    date_cols = [c for c in columns if c["udt_name"] in date_udts]
    minmax = []
    for c in date_cols:
        full = f'"{c["table_schema"]}"."{c["table_name"]}"'
        col = f'"{c["column_name"]}"'
        try:
            _, rows = q(f"SELECT MIN({col})::text AS min_v, MAX({col})::text AS max_v, COUNT({col}) AS n FROM {full}")
            r = rows[0]
            minmax.append({
                "schema": c["table_schema"],
                "table": c["table_name"],
                "column": c["column_name"],
                "type": c["udt_name"],
                "min": r["min_v"],
                "max": r["max_v"],
                "non_null": r["n"],
            })
            print(f"  {c['table_schema']}.{c['table_name']}.{c['column_name']}: {r['min_v']} -> {r['max_v']} (n={r['n']})")
        except Exception as e:
            minmax.append({
                "schema": c["table_schema"],
                "table": c["table_name"],
                "column": c["column_name"],
                "error": str(e),
            })
    dump("09_date_minmax", minmax)

    print("\n== column-name overlap (likely join keys) ==")
    name_to_tables: dict[str, list[str]] = {}
    for c in columns:
        name_to_tables.setdefault(c["column_name"], []).append(f'{c["table_schema"]}.{c["table_name"]}')
    overlaps = {n: ts for n, ts in name_to_tables.items() if len(ts) > 1}
    dump("10_name_overlap", overlaps)
    for n, ts in sorted(overlaps.items(), key=lambda kv: -len(kv[1])):
        print(f"  {n}: {ts}")

    print("\n== text-heavy columns (potential corpus) ==")
    text_like = [
        c for c in columns
        if c["udt_name"] in {"text", "varchar", "bpchar", "json", "jsonb"}
        or (c["character_maximum_length"] or 0) >= 1000
    ]
    text_stats = []
    for c in text_like:
        full = f'"{c["table_schema"]}"."{c["table_name"]}"'
        col = f'"{c["column_name"]}"'
        try:
            _, rows = q(
                f"SELECT AVG(length({col}::text))::int AS avg_len, "
                f"MAX(length({col}::text)) AS max_len, "
                f"COUNT({col}) AS non_null FROM {full}"
            )
            r = rows[0]
            text_stats.append({
                "schema": c["table_schema"], "table": c["table_name"],
                "column": c["column_name"], "udt": c["udt_name"],
                "avg_len": r["avg_len"], "max_len": r["max_len"],
                "non_null": r["non_null"],
            })
        except Exception as e:
            text_stats.append({
                "schema": c["table_schema"], "table": c["table_name"],
                "column": c["column_name"], "udt": c["udt_name"], "error": str(e),
            })
    text_stats.sort(key=lambda r: int(r.get("avg_len") or 0), reverse=True)
    dump("11_text_stats", text_stats)
    for r in text_stats[:25]:
        print(f"  {r.get('schema')}.{r.get('table')}.{r.get('column')} ({r.get('udt')}): avg={r.get('avg_len')} max={r.get('max_len')} non_null={r.get('non_null')}")

    print("\nDone.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
