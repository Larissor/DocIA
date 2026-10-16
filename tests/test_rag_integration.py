
import httpx
import chromadb
import pytest

from app.services.retrieval import retrieve_chunks
from app.services.generation import generate_answer, build_context


pytestmark = pytest.mark.integration

OLLAMA_URL = "http://localhost:11434"
EMBEDDING_MODEL = "nomic-embed-text"


def create_embedding(text: str) -> list[float]:
    """Gera embeddings usando o Ollama para os documentos de teste."""
    response = httpx.post(
        f"{OLLAMA_URL}/api/embed",
        json={
            "model": EMBEDDING_MODEL,
            "input": text,
        },
        timeout=60.0,
    )
    response.raise_for_status()

    data = response.json()
    embeddings = data.get("embeddings", [])

    if not embeddings or not embeddings[0]:
        raise RuntimeError(
            "O Ollama não retornou um embedding válido para o teste."
        )

    return embeddings[0]


def test_rag_integration():
    """Testa a recuperação de documentos e a geração de respostas."""

    # Cliente temporário: os dados são usados somente neste teste.
    client = chromadb.EphemeralClient()

    collection = client.create_collection(
        name="docia_integration_test"
    )

    documents = [
        {
            "id": "chunk-prazo",
            "text": (
                "O prazo para entrega dos equipamentos é de "
                "15 dias úteis após a aprovação do pedido."
            ),
            "metadata": {
                "document_id": "doc-teste-001",
                "filename": "contrato_teste.pdf",
                "page": 2,
            },
        },
        {
            "id": "chunk-horario",
            "text": (
                "O horário de funcionamento é das 8h às 17h, "
                "de segunda a sexta-feira."
            ),
            "metadata": {
                "document_id": "doc-teste-001",
                "filename": "contrato_teste.pdf",
                "page": 3,
            },
        },
        {
            "id": "chunk-pagamento",
            "text": (
                "O pagamento deverá ser realizado em até "
                "30 dias após a emissão da nota fiscal."
            ),
            "metadata": {
                "document_id": "doc-teste-001",
                "filename": "contrato_teste.pdf",
                "page": 4,
            },
        },
        {
            "id": "chunk-garantia",
            "text": (
                "Os equipamentos possuem garantia de "
                "12 meses a partir da data de entrega."
            ),
            "metadata": {
                "document_id": "doc-teste-001",
                "filename": "contrato_teste.pdf",
                "page": 5,
            },
        },
    ]

    # Cria embeddings e insere os trechos na coleção.
    embeddings = [
        create_embedding(document["text"])
        for document in documents
    ]

    collection.add(
        ids=[document["id"] for document in documents],
        documents=[document["text"] for document in documents],
        metadatas=[document["metadata"] for document in documents],
        embeddings=embeddings,
    )

    question = "Qual é o prazo para entrega dos equipamentos?"

    # 1. Testa a recuperação dos trechos.
    chunks = retrieve_chunks(
        question,
        collection,
        top_k=4,
    )

    assert chunks, "A recuperação não retornou nenhum trecho."
    assert len(chunks) <= 4

    retrieved_ids = [
        chunk["chunk_id"]
        for chunk in chunks
    ]

    assert "chunk-prazo" in retrieved_ids, (
        f"O trecho esperado não foi recuperado. "
        f"IDs encontrados: {retrieved_ids}"
    )

    expected_chunk = next(
        chunk
        for chunk in chunks
        if chunk["chunk_id"] == "chunk-prazo"
    )

    assert expected_chunk["filename"] == "contrato_teste.pdf"
    assert expected_chunk["page"] == 2

    # =========================================================
    # DIAGNÓSTICO TEMPORÁRIO
    # Remova esta seção depois de identificar o problema.
    # =========================================================

    print("\n" + "=" * 60)
    print("DIAGNÓSTICO TEMPORÁRIO — DocIA")
    print("=" * 60)

    print("\n=== PERGUNTA ===")
    print(question)

    print("\n=== CHUNKS RECUPERADOS ===")
    for index, chunk in enumerate(chunks, start=1):
        print(f"\nTrecho {index}")
        print(f"ID: {chunk.get('chunk_id')}")
        print(f"Arquivo: {chunk.get('filename')}")
        print(f"Página: {chunk.get('page')}")
        print(f"Distância: {chunk.get('distance')}")
        print(f"Conteúdo: {chunk.get('text')}")

    print("\n=== CONTEXTO ENVIADO AO MODELO ===")
    context = build_context(chunks)
    print(context)

    # =========================================================
    # GERAÇÃO DA RESPOSTA
    # =========================================================

    print("\n=== TESTE COM APENAS O TRECHO RELEVANTE ===")
    print(expected_chunk["text"])

    answer = generate_answer(question, [expected_chunk])

    print("\n=== RESPOSTA COM UM ÚNICO TRECHO ===")
    print(answer)

    print("\n" + "=" * 60)
    print("FIM DO DIAGNÓSTICO")
    print("=" * 60)

    # Verifica se o modelo respondeu com a informação esperada.
    normalized_answer = (
        answer.lower()
        .replace("-", " ")
    )

    assert answer.strip(), "O modelo retornou uma resposta vazia."

    assert (
        "15 dias úteis" in normalized_answer
        or "15 dias uteis" in normalized_answer
    ), (
        "A resposta não contém o prazo esperado. "
        f"Resposta recebida: {answer}"
    )

    client.delete_collection("docia_integration_test")
