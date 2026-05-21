def test_list_prompts(client) -> None:
    response = client.get("/api/v1/ai/prompts")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "default" in data["data"]
    assert "code_review" in data["data"]


def test_chat_mock(client) -> None:
    response = client.post(
        "/api/v1/ai/chat",
        json={"prompt": "Hello scaffold", "prompt_template": "default"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["content"]
