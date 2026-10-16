
import httpx
import pytest

from app.services import generation


def sample_chunks():
    return [
        {
            "chunk_id": "chunk-001",
            "document_id": "doc-001",
            "filename": "manual.pdf",
            "page": 3,
            "text": "O prazo para entrega é de 15 dias úteis.",
            "distance": 0.15,
        }
    ]


class MockResponse:
    def raise_for_status(self):
        pass

    def json(self):
        return {
            "message": {
                "content": "O prazo para entrega é de 15 dias úteis."
            }
        }


def test_build_context_contains_document_content():
    context = generation.build_context(sample_chunks())

    assert "O prazo para entrega é de 15 dias úteis." in context
    assert "manual.pdf" in context
    assert "Página: 3" in context


def test_empty_chunks_return_no_evidence_message():
    answer = generation.generate_answer(
        "Qual é o prazo?",
        [],
    )

    assert answer == generation.NO_EVIDENCE_MESSAGE


def test_empty_question_raises_error():
    with pytest.raises(ValueError):
        generation.generate_answer("   ", sample_chunks())


def test_generate_answer_calls_ollama(monkeypatch):
    captured = {}

    def fake_post(url, json, timeout):
        captured["url"] = url
        captured["payload"] = json
        captured["timeout"] = timeout
        return MockResponse()

    monkeypatch.setattr(generation.httpx, "post", fake_post)

    answer = generation.generate_answer(
        "Qual é o prazo para entrega?",
        sample_chunks(),
    )

    assert answer == "O prazo para entrega é de 15 dias úteis."
    assert captured["url"].endswith("/api/chat")
    assert captured["payload"]["model"] == generation.LLM_MODEL
    assert captured["payload"]["stream"] is False

    user_message = captured["payload"]["messages"][1]["content"]
    assert "Qual é o prazo para entrega?" in user_message
    assert "O prazo para entrega é de 15 dias úteis." in user_message


def test_ollama_connection_error_raises_runtime_error(monkeypatch):
    def fake_post(*args, **kwargs):
        raise httpx.ConnectError(
            "Conexão recusada",
            request=httpx.Request("POST", "http://localhost:11434/api/chat"),
        )

    monkeypatch.setattr(generation.httpx, "post", fake_post)

    with pytest.raises(RuntimeError, match="Não foi possível gerar"):
        generation.generate_answer(
            "Qual é o prazo?",
            sample_chunks(),
        )


def test_empty_model_response_raises_runtime_error(monkeypatch):
    class EmptyResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"message": {"content": ""}}

    monkeypatch.setattr(
        generation.httpx,
        "post",
        lambda *args, **kwargs: EmptyResponse(),
    )

    with pytest.raises(RuntimeError, match="resposta válida"):
        generation.generate_answer(
            "Qual é o prazo?",
            sample_chunks(),
        )
