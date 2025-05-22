import os
import boto3
from google.cloud import storage

# Configuration for S3 and GCS
S3_BUCKET_NAME = "your-s3-bucket-name"
GCS_BUCKET_NAME = "your-gcs-bucket-name"
LOCAL_STORAGE_PATH = "./results"  # Path to local storage for result artefacts

def migrate_to_s3():
    """Migrate result artefacts from local storage to S3."""
    s3_client = boto3.client("s3")
    for filename in os.listdir(LOCAL_STORAGE_PATH):
        if filename.endswith(".json"):
            file_path = os.path.join(LOCAL_STORAGE_PATH, filename)
            with open(file_path, "rb") as f:
                s3_client.upload_fileobj(f, S3_BUCKET_NAME, filename)
            print(f"Uploaded {filename} to S3 bucket {S3_BUCKET_NAME}")

def migrate_to_gcs():
    """Migrate result artefacts from local storage to GCS."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(GCS_BUCKET_NAME)
    for filename in os.listdir(LOCAL_STORAGE_PATH):
        if filename.endswith(".json"):
            file_path = os.path.join(LOCAL_STORAGE_PATH, filename)
            blob = bucket.blob(filename)
            blob.upload_from_filename(file_path)
            print(f"Uploaded {filename} to GCS bucket {GCS_BUCKET_NAME}")

if __name__ == "__main__":
    # Example usage: Choose S3 or GCS migration
    # migrate_to_s3()
    # migrate_to_gcs()
    print("Storage migration script created. Uncomment and configure to use.")
