
from app.services.generation import generate_answer

chunks = [
    {
        "chunk_id": "chunk-001",
        "document_id": "doc-001",
        "filename": "manual_teste.pdf",
        "page": 2,
        "text": "O horário de atendimento é das 8h às 17h, "
                "de segunda a sexta-feira.",
        "distance": 0.1,
    }
]

question = "Qual é o horário de atendimento?"

answer = generate_answer(question, chunks)

print("\nPergunta:", question)
print("Resposta:", answer)
