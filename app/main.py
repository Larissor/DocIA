from fastapi import FastAPI

app = FastAPI(
    title="DocIA",
    description="Assistente de documentos com RAG",
    version="0.1.0",
)

@app.get("/healt")
def health():
    return{"status":  "ok"}