from app.ingestion.loader import load_documents
from app.ingestion.cleaner import clean_document
from app.ingestion.chunker import chunk_documents



## Create the ingestion pipeline

## PDF/TXT → Load → Clean → Chunk
def run_ingestion():
    documents = load_documents("data/documents")

    cleaned_documents = []

    for document in documents:
        cleaned_documents.append(clean_document(document))

    chunks = chunk_documents(cleaned_documents)

    return chunks


if __name__ == "__main__":
    chunks = run_ingestion()

    print("Total chunks:", len(chunks))

    for chunk in chunks[:3]:
        print("\n--- CHUNK ---")
        print(chunk.content)
        print('-----METADATA--------')
        print("Metadata:", chunk.metadata)