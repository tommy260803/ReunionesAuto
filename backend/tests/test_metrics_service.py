import unittest
from unittest.mock import patch

from app.core.config import settings
from app.services.metrics_service import (
    finalize_async_invocation,
    finalize_invocation,
    record_transport,
    start_invocation,
)


class FakeSupabase:
    def __init__(self):
        self.rows = []

    def insert(self, table, rows):
        self.assert_table(table)
        self.rows.extend(dict(row) for row in rows)
        return rows

    def select(self, table, params):
        self.assert_table(table)
        rows = [row for row in self.rows if self._matches(row, params)]
        rows.sort(key=lambda row: row.get("started_at") or "", reverse=True)
        return rows[: int(params.get("limit", len(rows)))]

    def update(self, table, data, params):
        self.assert_table(table)
        updated = []
        for row in self.rows:
            if self._matches(row, params):
                row.update(data)
                updated.append(row)
        return updated

    @staticmethod
    def assert_table(table):
        if table != "metricas_n8n":
            raise AssertionError(table)

    @staticmethod
    def _matches(row, params):
        for key, expression in params.items():
            if key in {"select", "order", "limit", "offset"}:
                continue
            expected = expression.removeprefix("eq.")
            actual = row.get(key)
            if expected in {"true", "false"}:
                expected = expected == "true"
            if actual != expected:
                return False
        return True


class MetricTelemetryTests(unittest.TestCase):
    def setUp(self):
        self.sb = FakeSupabase()
        self.service_key_patch = patch.object(settings, "SUPABASE_SERVICE_ROLE_KEY", "")
        self.service_key_patch.start()

    def tearDown(self):
        self.service_key_patch.stop()

    def test_synchronous_invocation_uses_one_row(self):
        invocation = start_invocation(self.sb, "test_endpoint")
        record_transport(invocation, status_code=200, transport_latency_seconds=0.2)
        finalize_invocation(
            invocation,
            "success",
            status_code=200,
            transport_latency_seconds=0.2,
        )
        finalize_invocation(invocation, "error")

        self.assertEqual(len(self.sb.rows), 1)
        row = self.sb.rows[0]
        self.assertEqual(row["outcome"], "success")
        self.assertTrue(row["is_terminal"])
        self.assertEqual(row["transport_latency_seconds"], 0.2)
        self.assertGreaterEqual(row["end_to_end_latency_seconds"], 0)
        self.assertEqual(row["tiempo_respuesta"], row["end_to_end_latency_seconds"])

    def test_callback_finalizes_correlated_pending_invocation(self):
        invocation = start_invocation(
            self.sb,
            "async_endpoint",
            correlation_id="job-123",
        )
        record_transport(invocation, status_code=202, transport_latency_seconds=0.1)

        finalized = finalize_async_invocation(self.sb, "job-123", "success")

        self.assertTrue(finalized)
        self.assertEqual(len(self.sb.rows), 1)
        self.assertEqual(self.sb.rows[0]["outcome"], "success")
        self.assertTrue(self.sb.rows[0]["is_terminal"])
        self.assertIsNotNone(self.sb.rows[0]["end_to_end_latency_seconds"])

        second_finalization = finalize_async_invocation(self.sb, "job-123", "error")
        self.assertFalse(second_finalization)
        self.assertEqual(self.sb.rows[0]["outcome"], "success")

    def test_retry_cancels_previous_pending_invocation(self):
        start_invocation(self.sb, "async_endpoint", correlation_id="job-123")
        start_invocation(self.sb, "async_endpoint", correlation_id="job-123", attempt_number=2)

        self.assertEqual(len(self.sb.rows), 2)
        self.assertEqual(self.sb.rows[0]["outcome"], "cancelled")
        self.assertTrue(self.sb.rows[0]["is_terminal"])
        self.assertEqual(self.sb.rows[1]["outcome"], "pending")


if __name__ == "__main__":
    unittest.main()
