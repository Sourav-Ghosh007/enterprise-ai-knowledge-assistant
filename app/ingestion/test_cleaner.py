from app.ingestion.loader import load_documents
from app.ingestion.cleaner import clean_document

documents = load_documents("data/documents")

for document in documents:
    cleaned = clean_document(document)
    print(f"\n--- {cleaned.source} ---")
    print(cleaned.content[:500])