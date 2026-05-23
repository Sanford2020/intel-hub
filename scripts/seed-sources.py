#!/usr/bin/env python3
"""Import tier-0 sources into the API database."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SEED = ROOT / "seeds" / "tier-0-sources.json"


def _login(client: httpx.Client, base: str) -> None:
    email = os.environ.get("SMOKE_EMAIL", "admin@example.com")
    password = os.environ.get("SMOKE_PASSWORD", "change-me")
    response = client.post(
        f"{base}/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    response.raise_for_status()
    token = response.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed Intel Hub sources via API")
    parser.add_argument("--api", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--seed", default=str(DEFAULT_SEED), help="Path to tier-0 JSON")
    parser.add_argument("--replace", action="store_true", help="Update existing slugs")
    args = parser.parse_args()

    seed_path = Path(args.seed)
    if not seed_path.exists():
        raise SystemExit(f"Missing seed file: {seed_path}")

    sources = json.loads(seed_path.read_text(encoding="utf-8"))
    payload = {"sources": sources, "skip_existing": not args.replace}
    base = args.api.rstrip("/")
    url = f"{base}/api/v1/sources/import"

    with httpx.Client(timeout=120.0) as client:
        _login(client, base)
        resp = client.post(url, json=payload)
        if resp.status_code >= 400:
            print(resp.text, file=sys.stderr)
            resp.raise_for_status()
        print(resp.json())


if __name__ == "__main__":
    main()
