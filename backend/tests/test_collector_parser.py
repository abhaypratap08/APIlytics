"""Unit tests for the NGINX collector parser.

Pure functions — no DB, no HTTP. Verifies normalization and
deterministic event IDs.
"""
import importlib.util
from pathlib import Path

_COLLECTOR_PATH = Path(__file__).resolve().parents[2] / "collector" / "nginx_collector.py"
_spec = importlib.util.spec_from_file_location("nginx_collector", _COLLECTOR_PATH)
_collector = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_collector)

normalize_route = _collector.normalize_route
parse_line = _collector.parse_line


def test_normalize_strips_query_string():
    assert normalize_route("/api/orders?id=1") == "/api/orders"


def test_normalize_replaces_uuid():
    p = "/api/orders/1e8b9d2e-6b9f-4a7b-ae56-96a708aa11c4"
    assert normalize_route(p) == "/api/orders/{id}"


def test_normalize_replaces_numeric_id():
    assert normalize_route("/api/users/42") == "/api/users/{id}"
    assert normalize_route("/users/123/posts/456") == "/users/{id}/posts/{id}"


def test_normalize_keeps_static_paths():
    assert normalize_route("/") == "/"
    assert normalize_route("/index.html") == "/index.html"
    assert normalize_route("/api/search") == "/api/search"


def test_parse_line_returns_expected_shape():
    # Use a numeric ID because the collector only normalizes UUIDs and
    # pure numeric segments. Alphanumeric slugs (e.g. /orders/abc) are
    # left as-is — they might be meaningful route components like /orders/status.
    line = (
        '{"timestamp":"2026-11-11T14:31:05+00:00","method":"GET","path":"/api/orders/42",'
        '"status":200,"bytes_sent":34,"request_length":89,"latency_ms":0.123}'
    )
    ev = parse_line(line, 0)
    assert ev is not None
    assert ev["method"] == "GET"
    assert ev["route_template"] == "/api/orders/{id}"
    assert ev["status_code"] == 200
    assert ev["latency_ms"] == 123.0
    assert ev["request_size_bytes"] == 89
    assert ev["response_size_bytes"] == 34
    assert ev["service_name"] == "nginx"


def test_event_id_is_deterministic():
    line = (
        '{"timestamp":"2026-11-11T14:31:05+00:00","method":"GET","path":"/api/orders",'
        '"status":200,"bytes_sent":10,"request_length":10,"latency_ms":0.001}'
    )
    a = parse_line(line, 100)["event_id"]
    b = parse_line(line, 100)["event_id"]
    c = parse_line(line, 200)["event_id"]  # different offset → different id
    assert a == b
    assert a != c


def test_parse_line_rejects_garbage():
    assert parse_line("not json", 0) is None
    assert parse_line('{"incomplete":true}', 0) is None


def test_parse_line_rejects_empty():
    assert parse_line("", 0) is None
    assert parse_line("   \n", 0) is None
