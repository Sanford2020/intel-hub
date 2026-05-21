#!/usr/bin/env python3
"""One-off ingest smoke test for CISA source."""
import sys
import time

import httpx

SOURCE_ID = 40
BASE = "http://127.0.0.1:8000"


def main() -> None:
    client = httpx.Client(timeout=120.0)
    before = client.get(f"{BASE}/api/v1/stats/overview").json()["data"]["articles_total"]
    print(f"articles_before={before}")

    resp = client.post(
        f"{BASE}/api/v1/sources/{SOURCE_ID}/ingest",
        params={"async": True},
        timeout=60.0,
    )
    print(f"queue_status={resp.status_code} body={resp.text[:400]}")

    after = before
    last_log = None
    for i in range(30):
        time.sleep(4)
        after = client.get(f"{BASE}/api/v1/stats/overview").json()["data"]["articles_total"]
        logs = client.get(
            f"{BASE}/api/v1/sources/{SOURCE_ID}/ingest-logs",
            params={"page": 1, "page_size": 1},
        ).json()
        last_log = logs["data"][0] if logs.get("data") else None
        if last_log:
            print(
                f"t+{(i + 1) * 4}s articles={after} "
                f"log={last_log['status']} found={last_log['items_found']} "
                f"created={last_log['items_created']} skipped={last_log['items_skipped']}"
            )
        else:
            print(f"t+{(i + 1) * 4}s articles={after} no_log")

        if last_log and last_log["status"] in ("success", "partial", "failed"):
            break

    print(f"articles_after={after} delta={after - before}")
    if last_log:
        print(f"last_log_status={last_log['status']} error={last_log.get('error_message')}")

    if after <= before and (not last_log or last_log["status"] == "failed"):
        sys.exit(1)


if __name__ == "__main__":
    main()
