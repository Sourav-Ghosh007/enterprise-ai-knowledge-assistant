from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel, Field

import shutil
from pathlib import Path

from app.search.rag_service import ask_question
from app.api.upload_service import process_uploaded_file


# --------------------------------------------------
# FastAPI Application
# --------------------------------------------------

app = FastAPI(
    title="Enterprise AI Knowledge Assistant",
    description="RAG-based Enterprise Knowledge Assistant",
    version="1.0.0"
)


# --------------------------------------------------
# Request Model
# --------------------------------------------------

class AskRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="Question to ask the knowledge assistant"
    )


# --------------------------------------------------
# Response Model
# --------------------------------------------------

class AskResponse(BaseModel):
    question: str
    answer: str
    sources: list[str]


# --------------------------------------------------
# Home / Health Check
# --------------------------------------------------

@app.get("/")
def home():

    return {
        "status": "healthy",
        "message": "Enterprise AI Knowledge Assistant API is running"
    }


# --------------------------------------------------
# Ask Question
# --------------------------------------------------

@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):

    try:

        question = request.question.strip()

        if len(question) < 3:
            raise HTTPException(
                status_code=400,
                detail="Question must contain at least 3 characters."
            )

        answer, sources = ask_question(question)

        return {
            "question": question,
            "answer": answer,
            "sources": sources
        }

    except HTTPException:
        raise

    except Exception as e:

        print(f"Error while processing question: {e}")

        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your question."
        )


# --------------------------------------------------
# Upload Document
# --------------------------------------------------

@app.post("/upload")
def upload_document(file: UploadFile = File(...)):

    allowed_extensions = [".pdf", ".txt"]

    extension = Path(file.filename).suffix.lower()

    if extension not in allowed_extensions:

        raise HTTPException(
            status_code=400,
            detail="Only PDF and TXT files are supported."
        )


    # Create upload folder
    upload_folder = Path("data/uploads")

    upload_folder.mkdir(
        parents=True,
        exist_ok=True
    )


    # Save uploaded file
    file_path = upload_folder / file.filename


    try:

        with open(file_path, "wb") as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )


        # Process and index document
        result = process_uploaded_file(
            str(file_path)
        )


        return {
            "message": "Document uploaded and indexed successfully.",
            **result
        }


    except Exception as e:

        print(f"Upload error: {e}")

        raise HTTPException(
            status_code=500,
            detail="Failed to process and index document."
        )