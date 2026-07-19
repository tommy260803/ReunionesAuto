import unittest
from datetime import date, datetime, timezone

from fastapi import HTTPException

from app.metrics.router import _build_period_sample, _select_metric_period, get_n8n_statistics


class CappedFakeSupabase:
    def __init__(self, rows, server_cap=400):
        self.rows = rows
        self.server_cap = server_cap
        self.calls = []

    def select(self, table, params):
        self.calls.append((table, dict(params)))
        offset = int(params.get("offset", 0))
        requested = int(params.get("limit", 1000))
        size = min(requested, self.server_cap)
        return self.rows[offset : offset + size]


class PeriodFakeSupabase:
    def select(self, table, params):
        if int(params.get("offset", 0)) > 0:
            return []
        period = "a" if "2026-06-01" in params.get("and", "") else "b"
        base_latency = 2.0 if period == "a" else 1.0
        start_month = "06" if period == "a" else "07"
        rows = []
        for index in range(15):
            success = index < 10
            rows.append(
                {
                    "id": f"{period}-{index}",
                    "endpoint": "endpoint",
                    "started_at": f"2026-{start_month}-{index + 1:02d}T12:00:00Z",
                    "completed_at": f"2026-{start_month}-{index + 1:02d}T12:00:05Z",
                    "outcome": "success" if success else "error",
                    "end_to_end_latency_seconds": base_latency + index / 10 if success else 0.2,
                    "workflow_version": "test-v1",
                    "attempt_number": 1,
                }
            )
        return rows


class MetricRouterTests(unittest.TestCase):
    def test_period_query_paginates_past_server_cap(self):
        rows = [{"id": str(index)} for index in range(2505)]
        sb = CappedFakeSupabase(rows)
        start = datetime(2026, 6, 1, tzinfo=timezone.utc)
        end = datetime(2026, 7, 1, tzinfo=timezone.utc)

        selected, pages = _select_metric_period(sb, "endpoint", "production", start, end)

        self.assertEqual(len(selected), 2505)
        self.assertEqual(pages, 8)
        first_params = sb.calls[0][1]
        self.assertEqual(first_params["data_source"], "eq.production")
        self.assertEqual(first_params["is_terminal"], "eq.true")
        self.assertIn("started_at.gte.", first_params["and"])
        self.assertEqual(first_params["order"], "started_at.asc,id.asc")

    def test_period_sample_uses_only_successful_end_to_end_latency(self):
        rows = [
            {"outcome": "success", "end_to_end_latency_seconds": 1.25},
            {"outcome": "error", "end_to_end_latency_seconds": 0.1},
            {"outcome": "timeout", "end_to_end_latency_seconds": 90},
            {"outcome": "cancelled", "end_to_end_latency_seconds": 0.5},
            {"outcome": "success", "end_to_end_latency_seconds": None},
        ]
        start = datetime(2026, 6, 1, tzinfo=timezone.utc)
        end = datetime(2026, 7, 1, tzinfo=timezone.utc)

        sample = _build_period_sample("a", start, end, rows, 1)

        self.assertEqual(sample["latencies"], [1.25])
        self.assertEqual(sample["success"], 2)
        self.assertEqual(sample["failure"], 2)
        self.assertEqual(sample["metadata"].outcomes_excluded_unknown_status, 1)
        self.assertEqual(sample["metadata"].latencies_excluded_non_success, 3)
        self.assertEqual(sample["metadata"].latencies_excluded_missing, 1)
        self.assertEqual(len(sample["metadata"].dataset_sha256), 64)


class EndpointContractTests(unittest.IsolatedAsyncioTestCase):
    async def test_returns_valid_structured_analysis(self):
        response = await get_n8n_statistics(
            start_a=date(2026, 6, 1),
            end_a=date(2026, 6, 30),
            start_b=date(2026, 7, 1),
            end_b=date(2026, 7, 31),
            endpoint_filter="endpoint",
            data_source="production",
            admin={"is_admin": True},
            sb=PeriodFakeSupabase(),
        )

        self.assertEqual(response.metadata.data_source, "production")
        self.assertEqual(response.metadata.time_field, "started_at")
        self.assertEqual(response.t_test.status, "ok")
        self.assertEqual(response.t_test.n_a, 10)
        self.assertEqual(response.t_test.n_b, 10)
        self.assertEqual(response.chi_square.status, "ok")
        self.assertEqual(len(response.metadata.periods[0].dataset_sha256), 64)

    async def test_rejects_overlapping_periods(self):
        with self.assertRaises(HTTPException) as context:
            await get_n8n_statistics(
                start_a=date(2026, 6, 1),
                end_a=date(2026, 6, 30),
                start_b=date(2026, 6, 30),
                end_b=date(2026, 7, 15),
                endpoint_filter="endpoint",
                data_source="production",
                admin={"is_admin": True},
                sb=CappedFakeSupabase([]),
            )
        self.assertEqual(context.exception.status_code, 400)

    async def test_rejects_period_b_before_period_a(self):
        with self.assertRaises(HTTPException) as context:
            await get_n8n_statistics(
                start_a=date(2026, 7, 1),
                end_a=date(2026, 7, 31),
                start_b=date(2026, 6, 1),
                end_b=date(2026, 6, 30),
                endpoint_filter="endpoint",
                data_source="production",
                admin={"is_admin": True},
                sb=CappedFakeSupabase([]),
            )
        self.assertEqual(context.exception.status_code, 400)


if __name__ == "__main__":
    unittest.main()
