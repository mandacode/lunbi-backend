from fastapi.testclient import TestClient

from lunbi import main as main_module
from lunbi.api import deps as deps_module


class DummyPromptService:
    def __init__(self):
        self.calls = []

    def process_prompt(self, query: str):
        self.calls.append(query)
        return {
            "prompt_id": 42,
            "answer": "Test answer",
            "sources": ["doc.md"],
            "status": "success",
        }

    def answer_prompt(self, query: str):
        return {
            "answer": "Test answer",
            "sources": ["doc.md"],
            "status": "success",
        }

    def get_sample_prompts(self):
        return ["sample"]


def create_test_app(monkeypatch):
    monkeypatch.setattr(main_module, "init_db", lambda: None)
    app = main_module.create_app()
    return app


def test_prompt_endpoint(monkeypatch):
    app = create_test_app(monkeypatch)
    dummy_service = DummyPromptService()
    app.dependency_overrides[deps_module.get_prompt_service] = lambda: dummy_service

    client = TestClient(app)
    response = client.post("/prompts", json={"query": "Hello"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["prompt_id"] == 42
    assert payload["answer"] == "Test answer"
    assert payload["status"] == "success"
    assert dummy_service.calls == ["Hello"]


def test_sample_prompts_endpoint(monkeypatch):
    app = create_test_app(monkeypatch)
    dummy_service = DummyPromptService()
    app.dependency_overrides[deps_module.get_prompt_service] = lambda: dummy_service

    client = TestClient(app)
    response = client.get("/prompts/samples")

    assert response.status_code == 200
    payload = response.json()
    assert payload == {"prompts": ["sample"]}
