from dataclasses import dataclass

DEFAULT_REQUEST_THRESHOLD = 100


@dataclass
class ClientAggregate:
    client_id: str
    request_count: int
    window_seconds: int


@dataclass
class AbuseFinding:
    client_id: str
    request_count: int
    severity: str
    message: str


def detect_abuse(
    clients: list[ClientAggregate],
    request_threshold: int = DEFAULT_REQUEST_THRESHOLD,
) -> list[AbuseFinding]:

    findings = []

    for client in clients:
        if not client.client_id:
            continue

        if client.window_seconds <= 0 or client.request_count < 0:
            continue

        requests_per_minute = (
            client.request_count * 60 / client.window_seconds
        )

        if requests_per_minute >= request_threshold:
            findings.append(
                AbuseFinding(
                    client_id=client.client_id,
                    request_count=client.request_count,
                    severity=(
                        "HIGH"
                        if requests_per_minute >= request_threshold * 3
                        else "MEDIUM"
                    ),
                    message=(
                        f"Client generated approximately "
                        f"{requests_per_minute:.0f} requests per minute. "
                        "This may indicate unusually frequent activity."
                    ),
                )
            )

    return findings