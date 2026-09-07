import os
import hashlib

from dotenv import load_dotenv
from openai import AzureOpenAI
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

from app.ingestion.pipeline import run_ingestion


# --------------------------------------------------
# Load environment variables
# --------------------------------------------------

load_dotenv()


# --------------------------------------------------
# Azure OpenAI
# --------------------------------------------------

openai_client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-10-21"
)

embedding_deployment = os.getenv(
    "AZURE_OPENAI_EMBEDDING_DEPLOYMENT"
)


# --------------------------------------------------
# Azure AI Search
# --------------------------------------------------

search_client = SearchClient(
    endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
    index_name=os.getenv("AZURE_SEARCH_INDEX_NAME"),
    credential=AzureKeyCredential(
        os.getenv("AZURE_SEARCH_API_KEY")
    )
)


# --------------------------------------------------
# Generate Embedding
# --------------------------------------------------

def create_embedding(text: str) -> list[float]:

    response = openai_client.embeddings.create(
        input=text,
        model=embedding_deployment
    )

    return response.data[0].embedding


# --------------------------------------------------
# Create Unique Document ID
# --------------------------------------------------

def create_document_id(source: str, chunk_index: int) -> str:

    unique_text = f"{source}_{chunk_index}"

    document_id = hashlib.md5(
        unique_text.encode("utf-8")
    ).hexdigest()

    return document_id


# --------------------------------------------------
# Index Documents
# --------------------------------------------------

def index_documents():

    # Load → Clean → Chunk
    chunks = run_ingestion()

    documents = []

    for chunk in chunks:

        # Generate embedding
        embedding = create_embedding(
            chunk.content
        )

        # Create stable unique ID
        document_id = create_document_id(
            chunk.source,
            chunk.metadata["chunk_index"]
        )

        # Azure AI Search document
        document = {
            "id": document_id,
            "content": chunk.content,
            "source": chunk.source,
            "contentVector": embedding
        }

        documents.append(document)

    # Upload documents to Azure AI Search
    result = search_client.upload_documents(
        documents=documents
    )

    # Count successful uploads
    successful = sum(
        1 for item in result
        if item.succeeded
    )

    print("Total chunks:", len(chunks))
    print("Successfully indexed:", successful)


# --------------------------------------------------
# Run
# --------------------------------------------------

if __name__ == "__main__":
    index_documents()