'''
## This Upload service manually processes uploaded files, including loading, cleaning, chunking, 
# creating embeddings, and indexing them in Azure AI Search.


from pathlib import Path
import shutil

from app.ingestion.loader import load_documents
from app.ingestion.cleaner import clean_document
from app.ingestion.chunker import chunk_documents
from app.indexing.index_documents import create_embedding, create_document_id, search_client


UPLOAD_FOLDER = Path("data/uploads")


def process_uploaded_file(file_path: str):

    # ----------------------------------------------
    # 1. Load uploaded document
    # ----------------------------------------------

    documents = load_documents(str(Path(file_path).parent))

    # Find the uploaded document
    uploaded_name = Path(file_path).name

    documents = [
        document
        for document in documents
        if Path(document.source).name == uploaded_name
    ]

    if not documents:
        raise ValueError("Uploaded document could not be loaded.")


    # ----------------------------------------------
    # 2. Clean
    # ----------------------------------------------

    cleaned_documents = []

    for document in documents:
        cleaned_documents.append(
            clean_document(document)
        )


    # ----------------------------------------------
    # 3. Chunk
    # ----------------------------------------------

    chunks = chunk_documents(cleaned_documents)


    # ----------------------------------------------
    # 4. Create embeddings + Search documents
    # ----------------------------------------------

    search_documents = []

    for chunk in chunks:

        embedding = create_embedding(
            chunk.content
        )

        document_id = create_document_id(
            chunk.source,
            chunk.metadata["chunk_index"]
        )

        search_documents.append(
            {
                "id": document_id,
                "content": chunk.content,
                "source": chunk.source,
                "contentVector": embedding
            }
        )


    # ----------------------------------------------
    # 5. Upload to Azure AI Search
    # ----------------------------------------------

    results = search_client.upload_documents(
        documents=search_documents
    )

    successful = sum(
        1 for result in results
        if result.succeeded
    )


    return {
        "filename": uploaded_name,
        "chunks": len(chunks),
        "indexed": successful
    }

'''


### Now the below code will directly uploaded the file to Azure Blob Storage and then process it for indexing in Azure AI Search.
from pathlib import Path

from app.ingestion.loader import load_documents
from app.ingestion.cleaner import clean_document
from app.ingestion.chunker import chunk_documents
from app.indexing.index_documents import (
    create_embedding,
    create_document_id,
    search_client
)
from app.storage.blob_storage import upload_file


def process_uploaded_file(file_path: str):

    # --------------------------------------------------
    # 1. Upload original file to Azure Blob Storage
    # --------------------------------------------------

    blob_name = upload_file(file_path)

    # --------------------------------------------------
    # 2. Load the uploaded file for processing
    # --------------------------------------------------

    path = Path(file_path)

    documents = load_documents(str(path.parent))

    documents = [
        document
        for document in documents
        if Path(document.source).name == path.name
    ]

    if not documents:
        raise ValueError("Uploaded document could not be loaded.")

    # --------------------------------------------------
    # 3. Clean document
    # --------------------------------------------------

    cleaned_documents = []

    for document in documents:
        cleaned_documents.append(
            clean_document(document)
        )

    # --------------------------------------------------
    # 4. Create chunks
    # --------------------------------------------------

    chunks = chunk_documents(cleaned_documents)

    # --------------------------------------------------
    # 5. Create embeddings and Search documents
    # --------------------------------------------------

    search_documents = []

    for chunk in chunks:

        embedding = create_embedding(chunk.content)

        document_id = create_document_id(
            chunk.source,
            chunk.metadata["chunk_index"]
        )

        search_documents.append({
            "id": document_id,
            "content": chunk.content,
            "source": blob_name,
            "contentVector": embedding
        })

    # --------------------------------------------------
    # 6. Upload chunks to Azure AI Search
    # --------------------------------------------------

    results = search_client.upload_documents(
        documents=search_documents
    )

    successful = sum(
        1
        for result in results
        if result.succeeded
    )

    return {
        "filename": blob_name,
        "chunks": len(chunks),
        "indexed": successful
    }