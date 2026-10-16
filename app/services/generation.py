
import os

import httpx


OLLAMA_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://localhost:11434",
).rstrip("/")

LLM_MODEL = os.getenv(
    "LLM_MODEL",
    "llama3.2:1b",
)

NO_EVIDENCE_MESSAGE = (
    "Não encontrei evidências suficientes nos documentos "
    "disponíveis para responder a essa pergunta."
)


def build_context(chunks: list[dict]) -> str:
    """Monta o contexto usando somente o conteúdo dos documentos."""

    context_parts = []

    for chunk in chunks:
        text = chunk.get("text", "")

        if isinstance(text, str) and text.strip():
            context_parts.append(text.strip())

    return "\n\n---\n\n".join(context_parts)


def generate_answer(
    question: str,
    chunks: list[dict],
) -> str:
    """Gera uma resposta com base nos trechos recuperados pelo RAG."""

    if not question or not question.strip():
        raise ValueError("A pergunta não pode estar vazia.")

    if not chunks:
        return NO_EVIDENCE_MESSAGE

    context = build_context(chunks)

    if not context:
        return NO_EVIDENCE_MESSAGE

    prompt = f"""
Responda à pergunta usando o contexto abaixo.

Se a resposta estiver escrita no contexto, responda diretamente.
Não invente informações.
Não diga que faltam informações quando a resposta estiver explícita.
Se a resposta realmente não estiver no contexto, informe que não encontrou a informação.

CONTEXTO:
{context}

PERGUNTA:
{question.strip()}

RESPOSTA:
""".strip()

    payload = {
        "model": LLM_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0,
        },
    }

    try:
        response = httpx.post(
            f"{OLLAMA_URL}/api/generate",
            json=payload,
            timeout=120.0,
        )
        response.raise_for_status()
        data = response.json()

    except httpx.HTTPError as error:
        raise RuntimeError(
            "Não foi possível gerar a resposta. "
            "Verifique se o Ollama está em execução "
            "e se o modelo está disponível."
        ) from error

    except ValueError as error:
        raise RuntimeError(
            "O Ollama retornou uma resposta JSON inválida."
        ) from error

    if not isinstance(data, dict):
        raise RuntimeError(
            "O Ollama retornou uma resposta em formato inválido."
        )

    answer = data.get("response", "")

    if not isinstance(answer, str) or not answer.strip():
        raise RuntimeError(
            "O modelo não retornou uma resposta válida."
        )

    return answer.strip()
