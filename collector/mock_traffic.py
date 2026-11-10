import asyncio
import httpx
import random
import sys
import uuid
from datetime import datetime, timezone

API_BASE = "http://127.0.0.1:8000"
SESSION_ID = sys.argv[1]

async def main():
    print(f"Generating fake traffic for session {SESSION_ID}...")
    
    async with httpx.AsyncClient() as client:
        for i in range(30):
            # Randomize the behavior to look like a real broken site
            r = random.random()
            
            if r < 0.5:
                # 50% Healthy traffic
                status, failure, latency = 200, None, random.uniform(15, 50)
                route = "/api/catalog/search"
            elif r < 0.8:
                # 30% Server Errors
                status, failure, latency = 500, None, random.uniform(200, 500)
                route = "/api/checkout/process"
            elif r < 0.95:
                # 15% Client Errors (404s)
                status, failure, latency = 404, None, random.uniform(10, 30)
                route = "/api/catalog/item/99999"
            else:
                # 5% Network Failures (Total drop)
                status, failure, latency = None, "net::ERR_CONNECTION_REFUSED", 0.0
                route = "/api/auth/login"

            event = {
                "event_id": str(uuid.uuid4()),
                "source_type": "browser_sandbox",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "origin_host": "broken-ecommerce.com",
                "method": "GET" if r < 0.8 else "POST",
                "route_template": route,
                "resource_type": "fetch",
                "status_code": status,
                "failure_kind": failure,
                "latency_ms": latency,
            }

            # Send to backend
            await client.post(
                f"{API_BASE}/api/v1/internal/sandbox-sessions/{SESSION_ID}/events",
                json={"events": [event]}
            )
            
            print(f"Sent {event['method']} {route} -> Status: {status} (Failure: {failure})")
            
            # Small delay to simulate network timing and show live UI updates
            await asyncio.sleep(0.2)

    print("Finished generating fake traffic!")

if __name__ == "__main__":
    asyncio.run(main())
