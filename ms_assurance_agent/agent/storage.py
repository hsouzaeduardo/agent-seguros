import os
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
from uuid import uuid4

load_dotenv()

blob_service_client = BlobServiceClient.from_connection_string(os.getenv("AZURE_STORAGE_CONNECTION_STRING"))
container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME")

def upload_image_to_blob(file, filename):
    print(f"Uploading {filename} to Azure Blob Storage...")
    print(f"Container: {container_name}")
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=filename)
    blob_client.upload_blob(file, overwrite=True)
    return blob_client.url
