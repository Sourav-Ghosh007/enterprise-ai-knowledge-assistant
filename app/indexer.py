import os
from dotenv import load_dotenv
from openai import AzureOpenAI
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

load_dotenv()

# ---------- Azure OpenAI ----------
openai_client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-10-21"
)

embedding_deployment = os.getenv(
    "AZURE_OPENAI_EMBEDDING_DEPLOYMENT"
)

# ---------- Azure AI Search ----------
search_client = SearchClient(
    endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
    index_name=os.getenv("AZURE_SEARCH_INDEX_NAME"),
    credential=AzureKeyCredential(
        os.getenv("AZURE_SEARCH_API_KEY")
    )
)

# ---------- Text ----------
text = "Employees receive 18 annual paid leave days."

# ---------- Generate embedding ----------
response = openai_client.embeddings.create(
    input=text,
    model=embedding_deployment
)

embedding = response.data[0].embedding

print("Embedding length:", len(embedding))

# ---------- Upload document ----------
document = {
    "id": "1",
    "content": text,
    "source": "employee_handbook.txt",
    "contentVector": embedding
}

result = search_client.upload_documents(
    documents=[document]
)

print("Upload result:", result)