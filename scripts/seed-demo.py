import httpx

c = httpx.Client(timeout=30)
b = "http://127.0.0.1:8000/api/v1"
sid = c.get(b + "/sources").json()["data"][0]["id"]
for i, t in enumerate(
    [
        "China Taiwan geopolitics talks intensify",
        "OpenAI announces new AI chip partnership",
    ],
    1,
):
    a = c.post(
        b + "/articles",
        json={
            "source_id": sid,
            "title": t,
            "url": f"https://example.com/{i}",
            "content": "Regional tensions and technology supply chain shifts.",
        },
    )
    print("article", i, a.status_code)
    if a.status_code == 201:
        aid = a.json()["id"]
        c.post(b + f"/articles/{aid}/analyze")
c.post(
    b + "/alerts/rules",
    json={
        "name": "Geopolitics Watch",
        "keywords": ["geopolitics", "Taiwan", "AI"],
        "match_in": "all",
        "channel": "log",
    },
)
print("stats", c.get(b + "/stats/overview").json()["data"])
print("events", c.get(b + "/alerts/events").json()["total"])
