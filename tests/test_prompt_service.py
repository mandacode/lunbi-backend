import pytest

from lunbi.prompt_service import PromptService
from lunbi.models import PromptStatus


class DummyRepository:
    def __init__(self):
        self.saved = []
        self._counter = 0

    def add(self, prompt):
        self._counter += 1
        prompt.id = self._counter
        self.saved.append(prompt)
        return prompt


def test_process_prompt_success(monkeypatch):
    def fake_answer(self, query):
        return {
            "answer": "Sample answer",
            "sources": ["doc1.md"],
            "status": PromptStatus.SUCCESS,
        }

    monkeypatch.setattr(PromptService, "answer_prompt", fake_answer)

    service = PromptService(repository=DummyRepository())
    response = service.process_prompt("What is gravity?")

    assert response["prompt_id"] == 1
    assert response["answer"] == "Sample answer"
    assert response["sources"] == ["doc1.md"]
    assert response["status"] == PromptStatus.SUCCESS.value


def test_process_prompt_unknown_status(monkeypatch):
    def fake_answer(self, query):
        return {
            "answer": "Unknown",
            "sources": [],
            "status": "mystery",
        }

    monkeypatch.setattr(PromptService, "answer_prompt", fake_answer)

    service = PromptService(repository=DummyRepository())
    response = service.process_prompt("Test")

    assert response["status"] == PromptStatus.SUCCESS.value


def test_get_sample_prompts():
    service = PromptService()
    prompts = service.get_sample_prompts()
    assert len(prompts) > 0
    assert all(isinstance(item, str) for item in prompts)
