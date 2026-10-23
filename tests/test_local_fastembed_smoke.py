"""Offline regression tests for the local, true-FastEmbed image preflight."""

import copy
import unittest

from scripts.verify_local_fastembed import BASE_URL, SYNTHETIC_TICKET, check, validate_base_url


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
            "embedding_provider": "fastembed",
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
            "trace": [{"node": i} for i in range(7)],
            "provider_used": "mock",
            "grounded": True,
            "citation_integrity": True,
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


class LocalFastEmbedSmokeTests(unittest.TestCase):
    def test_pass_checks_real_fastembed_not_hashing(self):
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
        with self.assertRaisesRegex(ValueError, "FastEmbed"):
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
        with self.assertRaisesRegex(ValueError, "seven-stage"):
            check(fake_fetch(data))

    def test_rejects_public_ingest_success(self):
        with self.assertRaisesRegex(ValueError, "not denied"):
            check(fake_fetch(responses(), ingest_status=200))

    def test_rejects_mismatched_evaluation(self):
        data = responses()
        data["/eval/results"]["evaluation_mode"] = "unknown"
        with self.assertRaisesRegex(ValueError, "evaluation"):
            check(fake_fetch(data))

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
