def test_create_agent_run(client) -> None:
    response = client.post(
        "/api/v1/agents/runs",
        json={"goal": "Echo hello world", "agent_role": "backend_engineer"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["status"] in ("completed", "paused", "running")
    assert body["data"]["id"]


def test_list_agent_tools(client) -> None:
    response = client.get("/api/v1/agents/tools")
    assert response.status_code == 200
    tools = response.json()["data"]
    names = [t["name"] for t in tools]
    assert "echo" in names
    assert "human_approval" in names
