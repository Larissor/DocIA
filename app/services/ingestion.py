from pathlib import Path
from uuid import uuid4

import fitz # PyMuPDF

# Tamanho máximo permitido: 10MB
MAX_FILME_SIZE = 10 * 1024 * 1024

# Extensões aceitas pelo DocIA
ALLOWED_EXTENSIONS = {".pdf", ".txt"}

def ingest_document(filename: str, file_bytes: bytes) -> list[dict]:
    """
    Valida um arquivo PDF ou TXT e extrai seu texto.

    Cada registro contém:
    - document_id: identificador único do documento
    - filename: nome original do arquivo
    - page: número da página (TXT usa página 1)
    - text: texto extraído
    """

    # 1. Validar o nome e a extensão
    if not filename or not filename.strip():
        raise ValueError("O nome do arquivo não pode estar vazio.")

    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError("Formato não permitido. Envie um arquivo PDF ou TXT.")

    # 2. Validar o conteúdo e o tamanho
    if not file_bytes:
        raise ValueError("O arquivo está vazio.")

    if len(file_bytes) > MAX_FILE_SIZE:
        raise ValueError("O arquivo ultrapassa o limite de 10 MB.")

    # Identificador único para este documento
    document_id = str(uuid4())

    # 3. Extrair o texto conforme o formato
    if extension == ".pdf":
        records = _extract_pdf(filename, file_bytes, document_id)
    else:
        records = _extract_txt(filename, file_bytes, document_id)

    # 4. Rejeitar arquivos sem texto extraível
    if not records:
        raise ValueError(
            "Não foi possível extrair texto do arquivo. "
            "Verifique se ele contém texto selecionável."
        )

    return records


def _extract_pdf(
    filename: str,
    file_bytes: bytes,
    document_id: str,
) -> list[dict]:
    """Extrai o texto de cada página de um PDF."""

    records = []

    try:
        with fitz.open(stream=file_bytes, filetype="pdf") as pdf:
            # Percorre as páginas começando pelo número 1
            for page_number, page in enumerate(pdf, start=1):
                text = page.get_text("text").strip()

                # Ignora páginas sem texto
                if not text:
                    continue

                records.append(
                    {
                        "document_id": document_id,
                        "filename": filename,
                        "page": page_number,
                        "text": text,
                    }
                )

    except (fitz.FileDataError, RuntimeError) as error:
        raise ValueError("O arquivo PDF é inválido ou não pode ser lido.") from error

    return records


def _extract_txt(
    filename: str,
    file_bytes: bytes,
    document_id: str,
) -> list[dict]:
    """Lê um arquivo TXT codificado em UTF-8."""

    try:
        text = file_bytes.decode("utf-8-sig").strip()
    except UnicodeDecodeError as error:
        raise ValueError("O arquivo TXT deve utilizar codificação UTF-8.") from error

    if not text:
        return []

    return [
        {
            "document_id": document_id,
            "filename": filename,
            "page": 1,
            "text": text,
        }
    ]