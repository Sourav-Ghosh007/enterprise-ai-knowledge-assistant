print("blob_storage.py started")

import os
from pathlib import Path

from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient


# --------------------------------------------------
# Load environment variables
# --------------------------------------------------

load_dotenv()


# --------------------------------------------------
# Azure Blob Storage Configuration
# --------------------------------------------------

connection_string = os.getenv(
    "AZURE_STORAGE_CONNECTION_STRING"
)

container_name = "documents"


# --------------------------------------------------
# Create Blob Service Client
# --------------------------------------------------

blob_service_client = BlobServiceClient.from_connection_string(
    connection_string
)


# --------------------------------------------------
# Upload File
# --------------------------------------------------

def upload_file(file_path: str):

    path = Path(file_path)

    blob_name = path.name

    blob_client = blob_service_client.get_blob_client(
        container=container_name,
        blob=blob_name
    )

    with open(path, "rb") as data:

        blob_client.upload_blob(
            data,
            overwrite=True
        )

    return blob_name


# --------------------------------------------------
# Test
# --------------------------------------------------

if __name__ == "__main__":

    file_path = "data/documents/HR_Policy.pdf"

    uploaded_file = upload_file(file_path)

    print("Successfully uploaded:", uploaded_file)