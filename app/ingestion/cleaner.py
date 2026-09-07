import re
from app.ingestion.document import Document


def clean_document(document: Document) -> Document:
    cleaned = re.sub(r"\s+", " ", document.content).strip()

    return Document(
        content=cleaned,
        source=document.source,
        metadata={**document.metadata, "cleaned": True}
    )