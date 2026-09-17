# Enterprise AI Knowledge Assistant

An enterprise-focused AI knowledge assistant built using **Python, FastAPI, Azure OpenAI, Azure AI Search, Azure Blob Storage, Azure Key Vault, RAG, and RAGAS**.

The application allows users to upload enterprise documents and ask natural-language questions. The system retrieves relevant information from the indexed documents and generates grounded answers using Azure OpenAI.

---

## 🚀 Project Overview

The goal of this project is to build a practical **Enterprise RAG (Retrieval-Augmented Generation) application**.

Users can:

- Upload PDF and TXT documents
- Process and clean document content
- Split documents into chunks
- Generate embeddings
- Store documents and vectors in Azure AI Search
- Perform hybrid search
- Retrieve relevant enterprise information
- Generate answers using Azure OpenAI
- Display sources used for the answer
- Evaluate RAG quality using RAGAS

---

## 🏗️ Architecture

```text
                    User
                     |
                     v
              FastAPI / Web UI
                     |
          +----------+----------+
          |                     |
          v                     v
      Upload File           Ask Question
          |                     |
          v                     v
    Document Processing     Query Embedding
          |                     |
          v                     v
       Chunking          Azure AI Search
          |              Hybrid Search
          v                     |
      Embeddings                v
          |              Relevant Chunks
          v                     |
   Azure AI Search              |
                                v
                         Azure OpenAI
                                |
                                v
                         Grounded Answer
                                |
                                v
                         Answer + Sources



RAG Pipeline

The project implements the following RAG pipeline:

Document Ingestion
        ↓
Text Extraction
        ↓
Cleaning
        ↓
Chunking
        ↓
Embedding Generation
        ↓
Azure AI Search Indexing
        ↓
Hybrid Retrieval
        ↓
Context Retrieval
        ↓
Azure OpenAI
        ↓
Grounded Answer



🛠️ Technology Stack Used
Programming
Python 3.12
FastAPI
Uvicorn
Generative AI
Azure OpenAI
Embeddings
LLM-based answer generation
Retrieval-Augmented Generation (RAG)
Search
Azure AI Search
Vector Search
Hybrid Search
HNSW vector indexing
Azure Services
Azure OpenAI
Azure AI Search
Azure Blob Storage
Azure Key Vault
Microsoft Entra ID
Evaluation
RAGAS
Faithfulness
Answer Relevancy
Context Precision
Context Recall
DevOps / Development
Docker
Git
GitHub



☁️ Azure Resources

The project uses the following Azure resources:

Service	Purpose
Azure OpenAI	Embeddings and answer generation
Azure AI Search	Vector and hybrid document retrieval
Azure Blob Storage	Document storage
Azure Key Vault	Secure secret management
Microsoft Entra ID	Authentication and authorization setup




🔐 Security

Sensitive credentials are not hard-coded into the application.

Azure OpenAI API credentials are stored in:

Azure Key Vault

The application uses:

DefaultAzureCredential()

to authenticate with Azure services during local development.

The .env file contains configuration values and is excluded from Git using .gitignore.

Never commit API keys, passwords, tokens, or other secrets to GitHub.





📂 Project Structure
enterprise-ai-knowledge-assistant/
│
├── app/
│   ├── api/
│   │   ├── auth.py
│   │   ├── main.py
│   │   └── upload_service.py
│   │
│   ├── embeddings/
│   │   └── embedder.py
│   │
│   ├── evaluation/
│   │   ├── evaluate_rag.py
│   │   └── evaluate_ragas.py
│   │
│   ├── indexing/
│   │   └── index_documents.py
│   │
│   ├── ingestion/
│   │   ├── chunker.py
│   │   ├── cleaner.py
│   │   ├── document.py
│   │   ├── loader.py
│   │   └── pipeline.py
│   │
│   ├── search/
│   │   ├── hybrid_search.py
│   │   ├── rag.py
│   │   ├── rag_answer.py
│   │   ├── rag_service.py
│   │   └── vector_search.py
│   │
│   ├── storage/
│   │   └── blob_storage.py
│   │
│   ├── ui/
│   │   └── index.html
│   │
│   ├── indexer.py
│   └── main.py
│
├── config/
│
├── data/
│   ├── documents/
│   ├── evaluation/
│   ├── structured/
│   └── uploads/
│
├── tests/
│
├── .dockerignore
├── .gitignore
├── Dockerfile
├── README.md
├── requirements.txt
└── .env




📄 Document Processing

The application currently supports:

.pdf
.txt

Documents are:

Uploaded
Stored locally during processing
Loaded
Cleaned
Split into chunks
Converted into embeddings
Indexed in Azure AI Search




🔎 Hybrid Search

The application uses Azure AI Search for retrieval.

Hybrid search combines:

Keyword Search
      +
Vector Search
      ↓
Relevant Documents

Vector search uses embeddings generated with:

text-embedding-3-small

The embedding dimension used in the project is:

1536

The vector index uses the:

HNSW

algorithm.




🤖 Answer Generation

Azure OpenAI generates answers using only the retrieved enterprise context.

The application instructs the model:

Answer only using the provided context.

Do not use outside knowledge.
Do not make up information.
Do not guess.

If the retrieved context does not contain enough information, the system returns:

I don't have enough information to answer that.




📊 RAG Evaluation

The project includes RAGAS-based evaluation.

The evaluation dataset contains five test questions covering different enterprise documents and use cases.

Metrics used:

Metric	Result
Faithfulness	1.0000
Answer Relevancy	0.7343
Context Precision	1.0000
Context Recall	1.0000
Evaluation Interpretation
Faithfulness = 1.00
Generated answers were fully supported by the retrieved context.
Answer Relevancy = 0.7343
Answers were reasonably relevant to the questions, with room for improving directness.
Context Precision = 1.00
Retrieved context was relevant to the questions.
Context Recall = 1.00
The required information was successfully retrieved.

Note: The evaluation dataset currently contains only five questions, so these results should be treated as a project-level baseline rather than a general performance measurement.





🖥️ User Interface

The project includes a simple web UI for non-technical users.

Users can:

Upload documents
Index documents
Enter questions
View AI-generated answers
View document sources

FastAPI Swagger documentation is also available for API testing.




🐳 Docker

The application has been containerized using Docker.

Build the image:

docker build -t enterprise-ai-knowledge-assistant .

Run the container:

docker run -d --name enterprise-rag-app -p 8000:8000 --env-file .env enterprise-ai-knowledge-assistant
Docker Authentication Note

The Docker image builds successfully.

During local container execution, the application attempts to access Azure Key Vault through DefaultAzureCredential.

The local Docker container does not automatically inherit the host machine's Azure CLI authentication session. Therefore, additional container authentication configuration would be required for a fully authenticated local Docker runtime.

The application's existing Azure Key Vault authentication implementation was intentionally left unchanged rather than hard-coding secrets or weakening the security design.




▶️ Local Development

Create and activate a virtual environment:

python -m venv .venv

Activate on Windows CMD:

.venv\Scripts\activate

Install dependencies:

pip install -r requirements.txt

Configure the required environment variables in:

.env

Start the FastAPI application:

uvicorn app.api.main:app --reload

Open the application:

http://127.0.0.1:8000/

Swagger:

http://127.0.0.1:8000/docs
🧪 Running RAGAS Evaluation

Run:

python -m app.evaluation.evaluate_ragas

The evaluation uses Azure OpenAI for the required LLM and embedding-based evaluation components.

🔑 Environment Configuration

Example configuration:

AZURE_OPENAI_ENDPOINT=...
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=...
AZURE_OPENAI_CHAT_DEPLOYMENT=...
AZURE_SEARCH_ENDPOINT=...
AZURE_SEARCH_INDEX_NAME=...
AZURE_SEARCH_API_KEY=...
AZURE_TENANT_ID=...
AZURE_ENTRA_CLIENT_ID=...

Actual secrets must never be committed to GitHub.




📚 Sample Documents

The project contains synthetic enterprise documents such as:

Employee Handbook
HR Policy
IT Security Policy
Incident Response Policy
Product Overview

These documents are used to demonstrate enterprise knowledge retrieval and RAG behavior.




🎯 Key Learning Outcomes

This project demonstrates practical experience with:

RAG architecture
Document ingestion
Text cleaning
Chunking strategies
Embeddings
Vector databases/search
Azure AI Search
Hybrid search
Azure OpenAI
Prompt grounding
Secure secret management
Azure Key Vault
FastAPI
REST APIs
Web UI integration
RAG evaluation
RAGAS
Docker
Git/GitHub
Azure cloud development




🚀 Future Improvements

Potential production enhancements include:

Fully integrated Microsoft Entra ID authentication
Role-Based Access Control (RBAC)
Managed Identity for Azure resources
Advanced document processing
OCR and image understanding
Re-ranking
Better evaluation datasets
Monitoring and observability
Conversation history
Enterprise-scale deployment
CI/CD pipeline
Azure-hosted deployment




👨‍💻 Project Status

Status: Core implementation completed

The project demonstrates an end-to-end enterprise RAG workflow using Azure services, from document ingestion and indexing through retrieval, grounded answer generation, evaluation, and containerization.


### One small correction before you save

Your Git status showed the file as:

```text
readme.md