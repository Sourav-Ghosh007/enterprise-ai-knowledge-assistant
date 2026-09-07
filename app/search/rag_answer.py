import os
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from openai import AzureOpenAI

load_dotenv()

# -----------------------------
# Azure OpenAI
# -----------------------------
openai_client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-10-21"
)

# -----------------------------
# Azure AI Search
# -----------------------------
search_client = SearchClient(
    endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
    index_name=os.getenv("AZURE_SEARCH_INDEX_NAME"),
    credential=AzureKeyCredential(
        os.getenv("AZURE_SEARCH_API_KEY")
    )
)

# -----------------------------
# User Query
# -----------------------------
query = "How many paid leave days do employees receive?"

# -----------------------------
# 1. Create query embedding
# -----------------------------
response = openai_client.embeddings.create(
    input=query,
    model=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
)

query_vector = response.data[0].embedding

# -----------------------------
# 2. Vector Search
# -----------------------------
vector_query = VectorizedQuery(
    vector=query_vector,
    k_nearest_neighbors=3,
    fields="contentVector"
)

results = search_client.search(
    search_text=query,              # keyword search
    vector_queries=[vector_query],  # vector search
    select=["content", "source"],
    top=3
)

# -----------------------------
# 3. Build context
# -----------------------------
context = ""

for result in results:
    context += f"""
Source: {result["source"]}
Content: {result["content"]}
---
"""

print("\nRetrieved Context:")
print(context)

# -----------------------------
# 4. Generate RAG answer
# -----------------------------
prompt = f"""
You are an enterprise AI assistant.

Answer the user's question using ONLY the information
provided in the context.

If the answer is not present in the context, say:
"I don't have enough information to answer that."

Context:
{context}

User Question:
{query}
"""

completion = openai_client.chat.completions.create(
    model=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT"),
    messages=[
        {
            "role": "system",
            "content": "You answer questions using retrieved enterprise documents."
        },
        {
            "role": "user",
            "content": prompt
        }
    ],
    temperature=1
)

answer = completion.choices[0].message.content

print("\nRAG Answer:")
print(answer)