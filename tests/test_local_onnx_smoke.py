"""Offline regression tests for the local, true-ONNX image preflight."""

import copy
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

from scripts.verify_local_onnx import (
    BASE_URL,
    SYNTHETIC_TICKET,
    WORKFLOW_STAGES,
    check,
    fetch_json,
    validate_base_url,
)


def responses():
    return {
        "/ready": {
            "readiness": "ready",
            "demo_mode": True,
            "index": {
                "ready": True,
                "records": 27,
                "indexed": 27,
            },
        },
        "/provider-health": {
            "embedding_provider": "onnx",
            "embedding_model": "BAAI/bge-small-en-v1.5",
            "demo_mode": True,
            "mock_mode": True,
            "live_provider_calls_enabled": False,
            "ingestion_enabled": False,
            "qdrant_mode": "local",
        },
        "/dataset-info": {"records": 27},
        "/eval/results": {"evaluation_mode": "deterministic_mock", "dataset": {"sample_size": 8}},
        "/triage": {
            "trace": [{"node": node, "status": "completed"} for node in WORKFLOW_STAGES],
            "provider_used": "mock",
            "grounded": True,
            "citation_integrity": True,
            "fallback_used": False,
            "degraded_mode": False,
            "next_action": "ask_for_order_id",
        },
        "/ingest": {},
    }


def fake_fetch(data, *, ingest_status=403, calls=None):
    def fetch(url, body):
        path = url.removeprefix(BASE_URL)
        if calls is not None:
            calls.append((path, body))
        if path == "/triage":
            assert body == SYNTHETIC_TICKET
        elif path == "/ingest":
            assert body == {"recreate": False, "sample_size": 1}
        else:
            assert body is None
        return (ingest_status if path == "/ingest" else 200), copy.deepcopy(data[path])

    return fetch


class LocalONNXSmokeTests(unittest.TestCase):
    def test_pass_checks_real_onnx_not_hashing(self):
        calls = []
        report = check(fake_fetch(responses(), calls=calls))
        self.assertEqual(report["result"], "pass")
        self.assertEqual(report["indexed_records"], 27)
        self.assertEqual(report["seven_node_trace"], 7)
        self.assertEqual(report["public_ingestion_http_status"], 403)
        self.assertEqual(
            [path for path, _ in calls],
            [
                "/ready",
                "/provider-health",
                "/dataset-info",
                "/eval/results",
                "/triage",
                "/ingest",
            ],
        )

    def test_rejects_hashing_provider_and_skips_mutation_probe(self):
        data = responses()
        data["/provider-health"]["embedding_provider"] = "hashing"
        calls = []
        with self.assertRaisesRegex(ValueError, "ONNX"):
            check(fake_fetch(data, calls=calls))
        self.assertNotIn("/ingest", [path for path, _ in calls])

    def test_rejects_ingestion_enabled_before_post(self):
        data = responses()
        data["/provider-health"]["ingestion_enabled"] = True
        calls = []
        with self.assertRaisesRegex(ValueError, "boundary"):
            check(fake_fetch(data, calls=calls))
        self.assertNotIn("/ingest", [path for path, _ in calls])

    def test_rejects_wrong_bounded_index(self):
        data = responses()
        data["/ready"]["index"]["indexed"] = 26
        with self.assertRaisesRegex(ValueError, "27/27"):
            check(fake_fetch(data))

    def test_rejects_broken_seven_node_trace(self):
        data = responses()
        data["/triage"]["trace"] = data["/triage"]["trace"][:6]
        with self.assertRaisesRegex(ValueError, "workflow/grounding"):
            check(fake_fetch(data))

    def test_rejects_public_ingest_success(self):
        with self.assertRaisesRegex(ValueError, "not denied"):
            check(fake_fetch(responses(), ingest_status=200))

    def test_rejects_mismatched_evaluation(self):
        data = responses()
        data["/eval/results"]["evaluation_mode"] = "unknown"
        with self.assertRaisesRegex(ValueError, "evaluation"):
            check(fake_fetch(data))

    def test_rejects_wrong_stage_order_and_incomplete_status(self):
        data = responses()
        data["/triage"]["trace"][2]["node"] = "normalize_message"
        with self.assertRaisesRegex(ValueError, "workflow/grounding"):
            check(fake_fetch(data))
        data = responses()
        data["/triage"]["trace"][3]["status"] = "pending"
        with self.assertRaisesRegex(ValueError, "workflow/grounding"):
            check(fake_fetch(data))

    def test_rejects_false_grounding_and_invalid_manual_review(self):
        for key, value in (
            ("grounded", False),
            ("citation_integrity", False),
            ("degraded_mode", True),
            ("fallback_used", True),
            ("next_action", "reply_to_customer"),
        ):
            with self.subTest(field=key):
                data = responses()
                data["/triage"][key] = value
                with self.assertRaisesRegex(ValueError, "workflow/grounding"):
                    check(fake_fetch(data))

    def test_rejects_unexpected_model(self):
        data = responses()
        data["/provider-health"]["embedding_model"] = "unreviewed-model"
        with self.assertRaisesRegex(ValueError, "boundary"):
            check(fake_fetch(data))

    def test_local_fetch_does_not_follow_redirect_to_other_port(self):
        # Both servers bind only to loopback: this test never needs the internet.
        hits = []

        class RedirectTarget(BaseHTTPRequestHandler):
            def do_GET(self):
                hits.append(self.path)
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'{"ok":true}')

            def log_message(self, *_args):
                pass

        target = ThreadingHTTPServer(("127.0.0.1", 0), RedirectTarget)

        class RedirectSource(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(302)
                self.send_header(
                    "Location",
                    f"http://127.0.0.1:{target.server_port}/untrusted",
                )
                self.end_headers()

            def log_message(self, *_args):
                pass

        source = ThreadingHTTPServer(("127.0.0.1", 0), RedirectSource)
        workers = [Thread(target=s.serve_forever, daemon=True) for s in (target, source)]
        try:
            for worker in workers:
                worker.start()
            status, body = fetch_json(f"http://127.0.0.1:{source.server_port}/ready")
            self.assertEqual(status, 302)
            self.assertEqual(body, {})
            self.assertEqual(hits, [])
        finally:
            for server in (source, target):
                server.shutdown()
                server.server_close()
            for worker in workers:
                worker.join(timeout=3)

    def test_refuses_nonloopback_or_ambiguous_urls(self):
        for url in (
            "https://127.0.0.1:17860",
            "http://1.2.3.4:17860",
            "http://127.0.0.1:17860@evil.example:17860",
            "http://127.0.0.1:17860/path",
            "http://127.0.0.1:17860/?x=y",
            "http://localhost",
        ):
            with self.subTest(url=url), self.assertRaises(ValueError):
                validate_base_url(url)
        self.assertEqual(validate_base_url(BASE_URL), BASE_URL)


if __name__ == "__main__":
    unittest.main()
