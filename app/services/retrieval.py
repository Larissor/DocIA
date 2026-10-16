
import httpx


OLLAMA_URL = "http://localhost:11434"
EMBEDDING_MODEL = "nomic-embed-text"
TOP_K = 4


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

    except httpx.HTTPError as error:
        raise RuntimeError(
            "Não foi possível gerar o embedding. "
            "Verifique se o Ollama está em execução."
        ) from error

    data = response.json()
    embeddings = data.get("embeddings", [])

    if not embeddings or not embeddings[0]:
        raise RuntimeError("O Ollama não retornou um embedding válido.")

    return embeddings[0]


def retrieve_chunks(
    question: str,
    collection,
    top_k: int = TOP_K,
) -> list[dict]:
    """
    Busca os chunks mais relevantes para uma pergunta.

    collection: coleção do ChromaDB que contém os chunks
    top_k: quantidade máxima de resultados
    """

    if not question or not question.strip():
        raise ValueError("A pergunta não pode estar vazia.")

    if top_k < 1:
        raise ValueError("top_k deve ser maior que zero.")

    # Evita consultar uma coleção sem documentos
    if collection.count() == 0:
        return []

    # 1. Transforma a pergunta em embedding
    query_embedding = create_query_embedding(question)

    # 2. Busca os chunks semanticamente mais próximos
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, collection.count()),
        include=["documents", "metadatas", "distances"],
    )

    # 3. Organiza os resultados em uma lista
    chunks = []

    ids = results.get("ids", [[]])[0]
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    for chunk_id, text, metadata, distance in zip(
        ids, documents, metadatas, distances
    ):
        if not text:
            continue

        metadata = metadata or {}

        chunks.append(
            {
                "chunk_id": chunk_id,
                "document_id": metadata.get("document_id"),
                "filename": metadata.get("filename"),
                "page": metadata.get("page"),
                "text": text,
                "distance": distance,
            }
        )

    return chunks
