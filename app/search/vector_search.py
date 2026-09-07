import os
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from openai import AzureOpenAI

load_dotenv()

# Azure OpenAI
openai_client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-10-21"
)

# Azure AI Search
search_client = SearchClient(
    endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
    index_name=os.getenv("AZURE_SEARCH_INDEX_NAME"),
    credential=AzureKeyCredential(
        os.getenv("AZURE_SEARCH_API_KEY")
    )
)

query = "How many paid leave days do employees receive?"

# Embed query
response = openai_client.embeddings.create(
    input=query,
    model=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
)

query_vector = response.data[0].embedding

# Vector search
vector_query = VectorizedQuery(
    vector=query_vector,
    k_nearest_neighbors=3,
    fields="contentVector"
)

results = search_client.search(
    search_text=None,
    vector_queries=[vector_query],
    select=["content", "source"]
)

for result in results:
    print("Score:", result["@search.score"])
    print("Content:", result["content"])
    print("Source:", result["source"])
    print("---")