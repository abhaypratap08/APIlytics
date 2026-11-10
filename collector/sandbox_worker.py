import asyncio
import re
import sys
import uuid
from datetime import datetime, timezone
from urllib.parse import urlparse

import httpx
from playwright.async_api import async_playwright

API_BASE = "http://127.0.0.1:8000"
SESSION_ID = sys.argv[1]
TARGET_URL = sys.argv[2]

def normalize_url(url: str) -> str:
    path = urlparse(url).path or "/"
    path = re.sub(r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}', '{id}', path)
    path = re.sub(r'(?<=/)\d+(?=/|$)', '{id}', path)
    return path

async def main():
    async with httpx.AsyncClient() as client:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            async def handle_response(response):
                req = response.request
                if req.resource_type not in ("fetch", "xhr", "document"):
                    return
                
                try:
                    status = response.status
                    timing = response.request.timing
                    latency = 0.0
                    if timing and timing.get("responseStart") and timing.get("requestStart"):
                        latency = max(0, timing["responseStart"] - timing["requestStart"])
                    
                    event = {
                        "event_id": str(uuid.uuid4()),
                        "source_type": "browser_sandbox",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "origin_host": req.url.split("/")[2] if "//" in req.url else "unknown",
                        "method": req.method,
                        "route_template": normalize_url(req.url),
                        "resource_type": req.resource_type,
                        "status_code": status,
                        "failure_kind": None,
                        "latency_ms": latency,
                    }
                    
                    # Send IMMEDIATELY to the backend
                    res = await client.post(
                        f"{API_BASE}/api/v1/internal/sandbox-sessions/{SESSION_ID}/events",
                        json={"events": [event]}
                    )
                    print(f"[Worker] Sent: {req.method} {req.url} -> {status} ({res.status_code})")

                except Exception as e:
                    print(f"[Worker] Error: {e}")

            page.on("response", handle_response)
            
            print(f"[Worker] Navigating to {TARGET_URL}...")
            try:
                await page.goto(TARGET_URL, wait_until="networkidle", timeout=20000)
                # Wait a bit for any delayed API calls to finish
                await asyncio.sleep(3)
            except Exception as e:
                print(f"[Worker] Navigation warning: {e}")

            await browser.close()
            print("[Worker] Finished capture session.")

if __name__ == "__main__":
    asyncio.run(main())
