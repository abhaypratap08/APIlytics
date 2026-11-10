"""
Rule-based detection — STARTER STUB.

Owner: Hariom Mani Tripathi. Interface designed with Abhay Pratap Singh.

These are simple, explainable rules — NOT ML, NOT tuned against real traffic.
Hariom replaces the bodies with tested implementations; the interface stays.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

TRAFFIC_SPIKE_MULTIPLIER = 3.0
TRAFFIC_MIN_SAMPLE = 10
ERROR_RATE_THRESHOLD_PCT = 20.0
ERROR_MIN_SAMPLE = 5
LATENCY_REGRESSION_MULTIPLIER = 2.5
LATENCY_MIN_SAMPLE = 5


@dataclass
class EndpointAggregate:
    method: str
    route_template: str
    request_count: int
    error_count: int
    avg_latency_ms: float
    p95_latency_ms: float

    @property
    def error_rate_pct(self) -> float:
        return (self.error_count / self.request_count * 100) if self.request_count else 0.0


@dataclass
class Finding:
    id: str
    type: str
    severity: str
    method: str
    route_template: str
    title: str
    message: str
    recommendation: str


def _key(method: str, route: str) -> tuple[str, str]:
    return (method, route)


def _index(aggs: Iterable[EndpointAggregate]) -> dict[tuple[str, str], EndpointAggregate]:
    return {_key(a.method, a.route_template): a for a in aggs}


def detect_findings(
    current: list[EndpointAggregate],
    baseline: list[EndpointAggregate],
    window: str,
) -> list[Finding]:
    findings: list[Finding] = []
    cur = _index(current)
    base = _index(baseline)

    for key, c in cur.items():
        method, route = key
        b = base.get(key)

        if b is not None and c.request_count >= TRAFFIC_MIN_SAMPLE:
            if b.request_count > 0 and c.request_count >= b.request_count * TRAFFIC_SPIKE_MULTIPLIER:
                ratio = c.request_count / b.request_count
                findings.append(Finding(
                    id=f"traffic-spike:{method}:{route}:{window}",
                    type="TRAFFIC_ANOMALY",
                    severity="HIGH" if ratio >= 5 else "MEDIUM",
                    method=method,
                    route_template=route,
                    title="Request volume is above baseline",
                    message=(
                        f"{c.request_count} requests vs baseline {b.request_count} "
                        f"({ratio:.1f}x) in the last {window}."
                    ),
                    recommendation=(
                        "Verify whether the increase is expected. "
                        "Consider a rate limit only if the volume is abusive."
                    ),
                ))

        if c.request_count >= ERROR_MIN_SAMPLE and c.error_rate_pct >= ERROR_RATE_THRESHOLD_PCT:
            findings.append(Finding(
                id=f"high-error-rate:{method}:{route}:{window}",
                type="HIGH_ERROR_RATE",
                severity="HIGH" if c.error_rate_pct >= 50 else "MEDIUM",
                method=method,
                route_template=route,
                title="Elevated 5xx error rate",
                message=(
                    f"{c.error_count} of {c.request_count} requests returned 5xx "
                    f"({c.error_rate_pct:.1f}%) in the last {window}."
                ),
                recommendation=(
                    "Inspect application logs and upstream dependencies for this endpoint. "
                    "A 5xx response is a symptom, not the root cause."
                ),
            ))

        if b is not None and c.request_count >= LATENCY_MIN_SAMPLE and b.p95_latency_ms > 0:
            if c.p95_latency_ms >= b.p95_latency_ms * LATENCY_REGRESSION_MULTIPLIER:
                ratio = c.p95_latency_ms / b.p95_latency_ms
                findings.append(Finding(
                    id=f"latency-regression:{method}:{route}:{window}",
                    type="LATENCY_REGRESSION",
                    severity="MEDIUM",
                    method=method,
                    route_template=route,
                    title="p95 latency regression",
                    message=(
                        f"p95 is {c.p95_latency_ms:.0f} ms vs baseline "
                        f"{b.p95_latency_ms:.0f} ms ({ratio:.1f}x) in the last {window}."
                    ),
                    recommendation=(
                        "Check recent deploys, DB queries, and downstream calls for this endpoint."
                    ),
                ))

    sev_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    findings.sort(key=lambda f: (sev_order.get(f.severity, 9), f.type, f.route_template))
    return findings
