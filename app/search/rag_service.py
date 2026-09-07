import os

from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from openai import AzureOpenAI


# Load environment variables
load_dotenv()


# --------------------------------------------------
# Azure OpenAI Client
# --------------------------------------------------

openai_client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-10-21"
)


# --------------------------------------------------
# Azure AI Search Client
# --------------------------------------------------

search_client = SearchClient(
    endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
    index_name=os.getenv("AZURE_SEARCH_INDEX_NAME"),
    credential=AzureKeyCredential(
        os.getenv("AZURE_SEARCH_API_KEY")
    )
)


# --------------------------------------------------
# RAG Function
# --------------------------------------------------

def ask_question(query: str):

    # ----------------------------------------------
    # 1. Create query embedding
    # ----------------------------------------------

    response = openai_client.embeddings.create(
        input=query,
        model=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
    )

    query_vector = response.data[0].embedding


    # ----------------------------------------------
    # 2. Hybrid Search
    # ----------------------------------------------

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


    # ----------------------------------------------
    # 3. Build context + collect sources
    # ----------------------------------------------

    context = ""

    sources = []


    for result in results:

        source = result["source"]
        content = result["content"]

        # Add document content to RAG context
        context += f"""
Source: {source}
Content: {content}
---
"""

        # Add source only once
        if source not in sources:
            sources.append(source)


    # ----------------------------------------------
    # 4. Create RAG prompt
    # ----------------------------------------------

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


    # ----------------------------------------------
    # 5. Generate answer using Azure OpenAI
    # ----------------------------------------------

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


    # ----------------------------------------------
    # 6. Return answer + sources
    # ----------------------------------------------

    return answer, sources