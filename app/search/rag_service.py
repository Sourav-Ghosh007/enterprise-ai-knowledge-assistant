## adds a relevance threshold so unrelated documents

import os

from dotenv import load_dotenv

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.core.credentials import AzureKeyCredential

from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery

from openai import AzureOpenAI


# Load environment variables
load_dotenv()


# --------------------------------------------------
# KEY VAULT
# --------------------------------------------------

key_vault_url = "https://enterprise-rag-kv-2026.vault.azure.net/"

credential = DefaultAzureCredential()

key_vault_client = SecretClient(
    vault_url=key_vault_url,
    credential=credential
)

openai_api_key = key_vault_client.get_secret(
    "AZURE-OPENAI-API-KEY"
).value


# --------------------------------------------------
# AZURE OPENAI
# --------------------------------------------------

openai_client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=openai_api_key,
    api_version="2024-10-21"
)

embedding_deployment = os.getenv(
    "AZURE_OPENAI_EMBEDDING_DEPLOYMENT"
)

chat_deployment = os.getenv(
    "AZURE_OPENAI_CHAT_DEPLOYMENT"
)


# --------------------------------------------------
# AZURE AI SEARCH
# --------------------------------------------------

search_client = SearchClient(
    endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
    index_name=os.getenv("AZURE_SEARCH_INDEX_NAME"),
    credential=AzureKeyCredential(
        os.getenv("AZURE_SEARCH_API_KEY")
    )
)


# --------------------------------------------------
# SETTINGS
# --------------------------------------------------

TOP_K = 3

# Minimum similarity score required
# to consider a document relevant.
RELEVANCE_THRESHOLD = 0.70


# --------------------------------------------------
# CREATE EMBEDDING
# --------------------------------------------------

def create_embedding(text: str) -> list[float]:

    response = openai_client.embeddings.create(
        input=text,
        model=embedding_deployment
    )

    return response.data[0].embedding


# --------------------------------------------------
# SEARCH DOCUMENTS
# --------------------------------------------------

def search_documents(question: str):

    question_embedding = create_embedding(question)

    vector_query = VectorizedQuery(
        vector=question_embedding,
        k_nearest_neighbors=TOP_K,
        fields="contentVector"
    )

    results = search_client.search(
        search_text=question,
        vector_queries=[vector_query],
        select=[
            "content",
            "source"
        ],
        top=TOP_K
    )

    documents = []

    for result in results:

        score = result.get("@search.score", 0)

        #if score >= RELEVANCE_THRESHOLD:

        documents.append({
            "content": result.get("content", ""),
            "source": result.get("source", ""),
            "score": result.get("@search.score", 0)
            })

    return documents


# --------------------------------------------------
# GENERATE ANSWER
# --------------------------------------------------

def generate_answer(question: str, documents: list):

    if not documents:

        return (
            "I don't have enough information to answer that."
        )

    context = "\n\n".join(
        document["content"]
        for document in documents
    )

    prompt = f"""
You are an enterprise knowledge assistant.

Answer the user's question ONLY using the provided context.

If the context does not contain enough information,
say exactly:

"I don't have enough information to answer that."

Do not use outside knowledge.
Do not make up information.
Do not guess.

Context:
{context}

Question:
{question}

Answer:
"""


    response = openai_client.chat.completions.create(
        model=chat_deployment,
        messages=[
            {
                "role": "system",
                "content": "You answer only from provided enterprise context."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=1
    )

    return response.choices[0].message.content.strip()


# --------------------------------------------------
# MAIN RAG FUNCTION
# --------------------------------------------------

def ask_question(question: str):

    documents = search_documents(question)

    answer = generate_answer(
        question,
        documents
    )

    sources = [
        document["source"]
        for document in documents
    ]

    return answer, sources

'''

## In this code below, the sources is also coming when we are not even 
## selecting the source file still giving the last source file name. That 
## we are correcting in above code


import os

from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient


# Load environment variables
load_dotenv()


key_vault_url = "https://enterprise-rag-kv-2026.vault.azure.net/"

credential = DefaultAzureCredential()

key_vault_client = SecretClient(
    vault_url=key_vault_url,
    credential=credential
)

openai_api_key = key_vault_client.get_secret(
    "AZURE-OPENAI-API-KEY"
).value

# --------------------------------------------------
# Azure OpenAI Client
# --------------------------------------------------

openai_client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=openai_api_key,
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
'''