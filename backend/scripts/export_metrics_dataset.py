"""Export the exact production rows used by a two-period analysis."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path

from app.core.supabase_client import get_supabase
from app.metrics.router import _select_metric_period


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--endpoint", required=True)
    parser.add_argument("--start-a", required=True, type=date.fromisoformat)
    parser.add_argument("--end-a", required=True, type=date.fromisoformat)
    parser.add_argument("--start-b", required=True, type=date.fromisoformat)
    parser.add_argument("--end-b", required=True, type=date.fromisoformat)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def utc_bounds(start: date, end: date) -> tuple[datetime, datetime]:
    if start > end:
        raise ValueError("El inicio de un periodo no puede ser posterior a su fin.")
    return (
        datetime.combine(start, time.min, tzinfo=timezone.utc),
        datetime.combine(end + timedelta(days=1), time.min, tzinfo=timezone.utc),
    )


def main() -> None:
    args = parse_args()
    start_a, end_a = utc_bounds(args.start_a, args.end_a)
    start_b, end_b = utc_bounds(args.start_b, args.end_b)
    if end_a > start_b:
        raise ValueError("El Periodo A debe finalizar antes de que comience el Periodo B.")

    sb = get_supabase(service_role=True)
    snapshot_at = datetime.now(timezone.utc)
    rows_a, _ = _select_metric_period(sb, args.endpoint, "production", start_a, end_a, snapshot_at)
    rows_b, _ = _select_metric_period(sb, args.endpoint, "production", start_b, end_b, snapshot_at)
    rows = [
        {"period": period, **row}
        for period, period_rows in (("A", rows_a), ("B", rows_b))
        for row in period_rows
    ]
    fields = [
        "period",
        "id",
        "endpoint",
        "started_at",
        "completed_at",
        "outcome",
        "end_to_end_latency_seconds",
        "workflow_version",
        "attempt_number",
        "data_source",
        "is_terminal",
    ]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    digest = hashlib.sha256(args.output.read_bytes()).hexdigest()
    manifest = {
        "protocol_version": "1.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "snapshot_at_utc": snapshot_at.isoformat(),
        "endpoint": args.endpoint,
        "data_source": "production",
        "period_a": {"start": args.start_a.isoformat(), "end": args.end_a.isoformat()},
        "period_b": {"start": args.start_b.isoformat(), "end": args.end_b.isoformat()},
        "rows": len(rows),
        "csv_sha256": digest,
    }
    manifest_path = args.output.with_suffix(args.output.suffix + ".manifest.json")
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Exportados {len(rows)} registros a {args.output}")
    print(f"SHA-256: {digest}")


if __name__ == "__main__":
    main()
