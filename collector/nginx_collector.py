#!/usr/bin/env python3
"""
APIlytics NGINX collector.

Owned by Abhay Pratap Singh (backend and integration).

Tails NGINX JSON access logs and ships events to APIlytics
/api/v1/ingest/events with a real integration credential.

Design:
- Resumes from a saved byte offset, so restarts don't re-send
- Uses uuid5(log_line + offset) for deterministic event_id → replay-safe
- Batches every BATCH_SIZE lines (or every FLUSH_INTERVAL seconds)
- Normalizes route_template: UUIDs and numeric IDs become {id}
- Never logs the credential; never sends request bodies (NGINX doesn't log them)

Env vars:
- API_BASE_URL       e.g. http://127.0.0.1:8000
- INTEGRATION_TOKEN  the raw token returned once at integration creation
- LOG_PATH           default ./nginx/logs/access.log
- STATE_PATH         default ./collector/.state.json
- BATCH_SIZE         default 50
- FLUSH_INTERVAL     default 2.0 seconds
"""
from __future__ import annotations

import json
import os
import re
import signal
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

import httpx

API_BASE_URL = os.environ.get("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
INTEGRATION_TOKEN = os.environ.get("INTEGRATION_TOKEN", "")
LOG_PATH = Path(os.environ.get("LOG_PATH", "nginx/logs/access.log"))
STATE_PATH = Path(os.environ.get("STATE_PATH", "collector/.state.json"))
BATCH_SIZE = int(os.environ.get("BATCH_SIZE", "50"))
FLUSH_INTERVAL = float(os.environ.get("FLUSH_INTERVAL", "2.0"))

_UUID_RE = re.compile(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}")
_NUM_RE = re.compile(r"(?<=/)\d+(?=/|$)")


def normalize_route(path: str) -> str:
    """Normalize an NGINX request path into a route template."""
    path = path.split("?", 1)[0] or "/"
    path = _UUID_RE.sub("{id}", path)
    path = _NUM_RE.sub("{id}", path)
    return path


def parse_line(line: str, offset: int) -> dict | None:
    """Parse one NGINX JSON log line into a telemetry event payload."""
    line = line.strip()
    if not line:
        return None
    try:
        rec = json.loads(line)
    except json.JSONDecodeError:
        return None

    try:
        ts = datetime.fromisoformat(rec["timestamp"]).astimezone(timezone.utc)
        status = int(rec["status"])
        latency_s = float(rec["latency_ms"])
        method = str(rec["method"]).upper()
        path = str(rec["path"])
    except (KeyError, TypeError, ValueError):
        return None

    # Deterministic event_id: same log line at same offset → same event_id.
    # This makes collector restarts safe against duplicates.
    seed = f"{offset}:{line}"
    event_id = str(uuid.uuid5(uuid.NAMESPACE_URL, seed))

    return {
        "event_id": event_id,
        "timestamp": ts.isoformat(),
        "method": method,
        "route_template": normalize_route(path),
        "source_type": "nginx",
        "status_code": status,
        "latency_ms": round(latency_s * 1000, 2),  # NGINX $request_time is seconds
        "request_size_bytes": int(rec["request_length"]) if rec.get("request_length") is not None else None,
        "response_size_bytes": int(rec["bytes_sent"]) if rec.get("bytes_sent") is not None else None,
        "service_name": "nginx",
    }


def load_state() -> dict:
    if STATE_PATH.exists():
        try:
            return json.loads(STATE_PATH.read_text())
        except Exception:
            pass
    return {"inode": None, "offset": 0}


def save_state(inode: int, offset: int) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps({"inode": inode, "offset": offset}))


def flush(client: httpx.Client, batch: list[dict]) -> bool:
    if not batch:
        return True
    try:
        r = client.post(
            f"{API_BASE_URL}/api/v1/ingest/events",
            headers={"Authorization": f"Bearer {INTEGRATION_TOKEN}"},
            json={"events": batch},
            timeout=10.0,
        )
        if r.status_code == 200:
            body = r.json()
            print(f"[collector] sent {len(batch)} accepted={body.get('accepted')} dup={body.get('duplicates')}",
                  flush=True)
            return True
        print(f"[collector] ingest failed HTTP {r.status_code}: {r.text[:200]}", file=sys.stderr, flush=True)
        return False
    except httpx.HTTPError as e:
        print(f"[collector] transport error: {e}", file=sys.stderr, flush=True)
        return False


def run() -> None:
    if not INTEGRATION_TOKEN:
        print("INTEGRATION_TOKEN env var is required.", file=sys.stderr)
        sys.exit(2)
    if not LOG_PATH.exists():
        print(f"Log file not found: {LOG_PATH}", file=sys.stderr)
        sys.exit(2)

    stopping = {"flag": False}

    def _sig(_s, _f):
        stopping["flag"] = True
    signal.signal(signal.SIGINT, _sig)
    signal.signal(signal.SIGTERM, _sig)

    state = load_state()
    inode = LOG_PATH.stat().st_ino
    offset = state["offset"] if state.get("inode") == inode else 0
    print(f"[collector] starting at offset {offset} (inode {inode})", flush=True)

    batch: list[dict] = []
    last_flush = time.monotonic()

    with httpx.Client() as client, LOG_PATH.open("rb") as f:
        f.seek(offset)
        while not stopping["flag"]:
            # Rotation check
            try:
                cur_inode = LOG_PATH.stat().st_ino
            except FileNotFoundError:
                time.sleep(0.5)
                continue
            if cur_inode != inode:
                print(f"[collector] rotation detected (inode {inode} -> {cur_inode})", flush=True)
                flush(client, batch)
                batch.clear()
                f.close()
                f = LOG_PATH.open("rb")
                inode = cur_inode
                offset = 0

            line = f.readline()
            if line:
                event = parse_line(line.decode("utf-8", errors="replace"), offset)
                offset = f.tell()
                if event is not None:
                    batch.append(event)
            else:
                time.sleep(0.2)

            if len(batch) >= BATCH_SIZE or (
                batch and (time.monotonic() - last_flush) >= FLUSH_INTERVAL
            ):
                if flush(client, batch):
                    batch.clear()
                    save_state(inode, offset)
                last_flush = time.monotonic()

        # Final flush on shutdown
        if batch:
            flush(client, batch)
            save_state(inode, offset)
        print("[collector] stopped", flush=True)


if __name__ == "__main__":
    run()
