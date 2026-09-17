import json
import os

from langchain_openai import AzureOpenAIEmbeddings

from dotenv import load_dotenv
from datasets import Dataset

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall
)

from ragas.llms import LangchainLLMWrapper
from langchain_openai import AzureChatOpenAI

from app.search.rag_service import search_documents, generate_answer


# --------------------------------------------------
# LOAD ENVIRONMENT VARIABLES
# --------------------------------------------------

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
# AZURE OPENAI FOR RAGAS
# --------------------------------------------------

azure_llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=openai_api_key,
    api_version="2024-10-21",
    azure_deployment=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT"),
    temperature=1
)


# Wrap Azure OpenAI for RAGAS
ragas_llm = LangchainLLMWrapper(azure_llm,bypass_temperature=True)
azure_embeddings = AzureOpenAIEmbeddings(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=openai_api_key,
    api_version="2024-10-21",
    azure_deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
)

# --------------------------------------------------
# EVALUATION DATASET
# --------------------------------------------------

DATASET_PATH = "data/evaluation/questions.jsonl"


def load_evaluation_dataset():

    questions = []
    answers = []
    contexts = []
    ground_truths = []

    with open(
        DATASET_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        for line in file:

            item = json.loads(line)

            question = item["question"]
            expected_answer = item["answer"]

            # Retrieve documents using our RAG system
            documents = search_documents(question)

            # Extract retrieved content
            context = [
                document["content"]
                for document in documents
            ]

            # Generate answer using our RAG system
            answer = generate_answer(
                question,
                documents
            )

            questions.append(question)
            answers.append(answer)
            contexts.append(context)
            ground_truths.append(expected_answer)

    return Dataset.from_dict(
        {
            "question": questions,
            "answer": answers,
            "contexts": contexts,
            "ground_truth": ground_truths
        }
    )


# --------------------------------------------------
# RUN RAGAS EVALUATION
# --------------------------------------------------

def run_evaluation():

    print("Loading evaluation dataset...")

    dataset = load_evaluation_dataset()

    print("Running RAGAS evaluation...")

    result = evaluate(
        dataset,
        metrics=[
            faithfulness,
            answer_relevancy,
            context_precision,
            context_recall
        ],
        llm=ragas_llm,
        embeddings=azure_embeddings,
        raise_exceptions=True
    )

    print("\n")
    print("=" * 70)
    print("RAGAS EVALUATION RESULTS")
    print("=" * 70)

    print(result)


# --------------------------------------------------
# MAIN
# --------------------------------------------------

if __name__ == "__main__":
    run_evaluation()