
import pytest

from app.services.ingestion import ingest_document


def test_ingest_txt():
    content = "O DocIA utiliza inteligência artificial.".encode("utf-8")

    records = ingest_document("exemplo.txt", content)

    assert len(records) == 1
    assert records[0]["filename"] == "exemplo.txt"
    assert records[0]["page"] == 1
    assert "inteligência artificial" in records[0]["text"]
    assert records[0]["document_id"]


def test_reject_empty_file():
    with pytest.raises(ValueError, match="vazio"):
        ingest_document("vazio.txt", b"")


def test_reject_unsupported_extension():
    with pytest.raises(ValueError, match="Formato não permitido"):
        ingest_document("arquivo.docx", b"conteudo")


def test_reject_txt_without_text():
    with pytest.raises(ValueError, match="Não foi possível extrair"):
        ingest_document("vazio.txt", b"   \n  ")


def test_reject_file_over_size_limit():
    content = b"a" * (10 * 1024 * 1024 + 1)

    with pytest.raises(ValueError, match="10 MB"):
        ingest_document("grande.txt", content)
