import os
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_key = os.getenv("AZURE_OPENAI_API_KEY")
deployment = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")

client = AzureOpenAI(
    azure_endpoint=endpoint,
    api_key=api_key,
    api_version="2024-10-21"
)

text = "Employees receive 18 annual paid leave days."

response = client.embeddings.create(
    input=text,
    model=deployment
)

embedding = response.data[0].embedding

print("Text:")
print(text)

print("\nEmbedding length:")
print(len(embedding))

print("\nFirst 10 values:")
print(embedding[:10])