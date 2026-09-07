import os
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from openai import AzureOpenAI

load_dotenv()

openai_client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-10-21"
)

search_client = SearchClient(
    endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
    index_name=os.getenv("AZURE_SEARCH_INDEX_NAME"),
    credential=AzureKeyCredential(
        os.getenv("AZURE_SEARCH_API_KEY")
    )
)

query = "How many paid leave days do employees receive?"

# Create query embedding
response = openai_client.embeddings.create(
    input=query,
    model=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
)

query_vector = response.data[0].embedding

# Hybrid search
vector_query = VectorizedQuery(
    vector=query_vector,
    k_nearest_neighbors=3,
    fields="contentVector"
)

results = search_client.search(
    search_text=query,
    vector_queries=[vector_query],
    select=["content", "source"],
    top=3
)

# Build context
context = ""

for result in results:
    context += result["content"] + "\n"

# Generate answer
prompt = f"""
Answer the question using only the context below.

Context:
{context}

Question:
{query}
"""

answer = openai_client.chat.completions.create(
    model=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT"),
    messages=[
        {
            "role": "system",
            "content": "You are a helpful company knowledge assistant."
        },
        {
            "role": "user",
            "content": prompt
        }
    ],
    temperature=0
)

print(f"Answer: {answer.choices[0].message.content}")
#print(answer.choices[0].message.content)