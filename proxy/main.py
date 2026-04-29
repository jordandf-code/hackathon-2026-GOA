"""Read-only SQL proxy for the recon recon database.

Exposes a single POST /query endpoint that accepts
{"sql": str, "params": list?, "limit": int?} with a bearer token, runs the
statement against DATABASE_URL in a read-only psycopg2 session, and returns
JSON {columns, rows, row_count, truncated, elapsed_ms}.

Hardening:
 - bearer token via PROXY_TOKEN env var
 - psycopg2 set_session(readonly=True, autocommit=True)
 - SET statement_timeout (default 30s)
 - allowed first keywords: SELECT, WITH, SHOW, EXPLAIN, TABLE, VALUES
 - rejects multi-statement input (any ";" after stripping trailing ones)
 - row cap (default 10k) so a runaway query can't blow up the response
"""
from __future__ import annotations

import os
import re
import time
from datetime import date, datetime, time as dtime
from decimal import Decimal
from typing import Any

import psycopg2
import psycopg2.extras
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

DSN = os.environ["DATABASE_URL"]
TOKEN = os.environ["PROXY_TOKEN"]
MAX_ROWS = int(os.environ.get("MAX_ROWS", "10000"))
STATEMENT_TIMEOUT_MS = int(os.environ.get("STATEMENT_TIMEOUT_MS", "30000"))

_ALLOWED_FIRST = re.compile(
    r"^(?:\s|--[^\n]*\n|/\*.*?\*/)*"
    r"(SELECT|WITH|SHOW|EXPLAIN|TABLE|VALUES)\b",
    re.IGNORECASE | re.DOTALL,
)

app = FastAPI(title="pg-recon-proxy")


class QueryReq(BaseModel):
    sql: str
    params: list[Any] | None = None
    limit: int | None = None


def _check_auth(authorization: str | None) -> None:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="missing bearer token")
    if authorization.removeprefix("Bearer ").strip() != TOKEN:
        raise HTTPException(status_code=401, detail="bad token")


def _is_read_only(sql: str) -> bool:
    s = sql.strip()
    while s.endswith(";"):
        s = s[:-1].rstrip()
    if ";" in s:
        return False
    return bool(_ALLOWED_FIRST.match(s))


def _jsonable(v: Any) -> Any:
    if isinstance(v, (datetime, date, dtime)):
        return v.isoformat()
    if isinstance(v, Decimal):
        return str(v)
    if isinstance(v, (bytes, memoryview)):
        try:
            return bytes(v).decode("utf-8", errors="replace")
        except Exception:
            return repr(v)
    return v


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/query")
def query(req: QueryReq, authorization: str | None = Header(None)):
    _check_auth(authorization)
    if not _is_read_only(req.sql):
        raise HTTPException(
            status_code=400,
            detail="only single read-only statements allowed (SELECT/WITH/SHOW/EXPLAIN/TABLE/VALUES, no semicolons)",
        )
    cap = min(req.limit or MAX_ROWS, MAX_ROWS)
    conn = psycopg2.connect(DSN, connect_timeout=10)
    try:
        conn.set_session(readonly=True, autocommit=True)
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(f"SET statement_timeout = {STATEMENT_TIMEOUT_MS}")
        t0 = time.time()
        cur.execute(req.sql, req.params or None)
        cols = [c.name for c in cur.description] if cur.description else []
        rows: list[dict] = []
        truncated = False
        if cur.description:
            for i, row in enumerate(cur):
                if i >= cap:
                    truncated = True
                    break
                rows.append({k: _jsonable(v) for k, v in row.items()})
        elapsed_ms = int((time.time() - t0) * 1000)
        return JSONResponse(
            {
                "columns": cols,
                "rows": rows,
                "row_count": len(rows),
                "truncated": truncated,
                "elapsed_ms": elapsed_ms,
            }
        )
    except psycopg2.Error as e:
        raise HTTPException(status_code=400, detail=f"postgres error: {e.__class__.__name__}: {e}")
    finally:
        conn.close()
