
import os

import httpx


OLLAMA_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://localhost:11434",
).rstrip("/")

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "nomic-embed-text",
)

TOP_K = int(os.getenv("TOP_K", "4"))


def create_query_embedding(question: str) -> list[float]:
    """Transforma a pergunta em um vetor usando o Ollama."""

    if not question or not question.strip():
        raise ValueError("A pergunta não pode estar vazia.")

    try:
        response = httpx.post(
            f"{OLLAMA_URL}/api/embed",
            json={
                "model": EMBEDDING_MODEL,
                "input": question.strip(),
            },
            timeout=60.0,
        )
        response.raise_for_status()
        data = response.json()

    except httpx.HTTPError as error:
        raise RuntimeError(
            "Não foi possível gerar o embedding. "
            "Verifique a conexão com o Ollama e o modelo configurado."
        ) from error

    except ValueError as error:
        raise RuntimeError(
            "O Ollama retornou uma resposta JSON inválida."
        ) from error

    embeddings = data.get("embeddings", [])

    if (
        not embeddings
        or not isinstance(embeddings[0], list)
        or not embeddings[0]
    ):
        raise RuntimeError(
            "O Ollama não retornou um embedding válido."
        )

    return embeddings[0]


def retrieve_chunks(
    question: str,
    collection,
    top_k: int = TOP_K,
) -> list[dict]:
    """Recupera os chunks mais relevantes para uma pergunta."""

    if not question or not question.strip():
        raise ValueError("A pergunta não pode estar vazia.")

    if not isinstance(top_k, int) or isinstance(top_k, bool) or top_k < 1:
        raise ValueError("top_k deve ser um inteiro maior que zero.")

    total_chunks = collection.count()

    if total_chunks == 0:
        return []

    query_embedding = create_query_embedding(question)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, total_chunks),
        include=["documents", "metadatas", "distances"],
    )

    ids = results.get("ids", [[]])[0]
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    chunks = []

    for chunk_id, text, metadata, distance in zip(
        ids, documents, metadatas, distances
    ):
        if not text or not text.strip():
            continue

        metadata = metadata or {}

        chunks.append({
            "chunk_id": chunk_id,
            "document_id": metadata.get("document_id"),
            "filename": metadata.get("filename"),
            "page": metadata.get("page"),
            "text": text,
            "distance": distance,
        })

    return chunks