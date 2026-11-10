def estimate_cost(
    request_count: int,
    cost_per_1000_requests: float,
) -> float:

    if request_count < 0:
        raise ValueError("request_count cannot be negative")

    if cost_per_1000_requests < 0:
        raise ValueError("cost rate cannot be negative")

    return (request_count / 1000) * cost_per_1000_requests


def estimate_endpoint_costs(
    endpoints: list,
    cost_per_1000_requests: float,
) -> list[dict]:

    results = []

    for endpoint in endpoints:
        cost = estimate_cost(
            endpoint.request_count,
            cost_per_1000_requests,
        )

        results.append({
            "method": endpoint.method,
            "route_template": endpoint.route_template,
            "request_count": endpoint.request_count,
            "estimated_cost": round(cost, 6),
        })

    return results