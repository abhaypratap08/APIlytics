import pytest
from pydantic import ValidationError
from app.schemas.telemetry import TelemetryEventIn

VALID_EVENT = {
    "event_id": "1e8b9d2e-6b9f-4a7b-ae56-96a708aa11c4",
    "timestamp": "2026-10-11T06:30:00Z",
    "method": "get",
    "route_template": "/api/orders/{id}",
    "status_code": 200,
    "latency_ms": 184.5,
    "request_size_bytes": 1240,
    "response_size_bytes": 4820,
    "client_id": "client_42",
    "service_name": "orders-api",
}


def test_valid_event_parses_and_uppercases_method():
    event = TelemetryEventIn(**VALID_EVENT)
    assert event.method == "GET"


def test_invalid_status_code_rejected():
    with pytest.raises(ValidationError):
        TelemetryEventIn(**{**VALID_EVENT, "status_code": 99})


def test_negative_latency_rejected():
    with pytest.raises(ValidationError):
        TelemetryEventIn(**{**VALID_EVENT, "latency_ms": -1})


def test_missing_timezone_rejected():
    with pytest.raises(ValidationError):
        TelemetryEventIn(**{**VALID_EVENT, "timestamp": "2026-10-11T06:30:00"})


def test_malformed_uuid_rejected():
    with pytest.raises(ValidationError):
        TelemetryEventIn(**{**VALID_EVENT, "event_id": "not-a-uuid"})


def test_route_must_start_with_slash():
    with pytest.raises(ValidationError):
        TelemetryEventIn(**{**VALID_EVENT, "route_template": "api/orders"})
