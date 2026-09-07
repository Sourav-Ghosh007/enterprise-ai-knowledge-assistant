from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.ingestion.document import Document


def chunk_documents(documents: list[Document], chunk_size: int = 500, chunk_overlap: int = 50) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""]
    )

    chunks = []

    for document in documents:
        texts = splitter.split_text(document.content)

        for index, text in enumerate(texts):
            metadata = {
                **document.metadata,
                "chunk_index": index,
                "total_chunks": len(texts)
            }

            chunks.append(
                Document(
                    content=text,
                    source=document.source,
                    metadata=metadata
                )
            )

    return chunks


if __name__ == "__main__":
    from app.ingestion.loader import load_documents

    documents = load_documents("data/documents")
    chunks = chunk_documents(documents)

    print(f"Documents: {len(documents)}")
    print(f"Chunks: {len(chunks)}")

    for chunk in chunks[:5]:
        print(f"\n--- {chunk.metadata} ---")
        print(chunk.content)