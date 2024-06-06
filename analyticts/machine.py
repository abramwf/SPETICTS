import os
from google.cloud.storage import Client, transfer_manager

def download_bucket_with_transfer_manager(
    bucket_name, destination_directory="", workers=4, max_results=1000
):
    """Download all of the blobs in a bucket concurrently using a process pool."""

    # Set the environment variable for credentials
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "C:\\Users\\FARID\\OneDrive - Universitas Airlangga\\!Semester 6\\BANGKIT-ACADEMY\\Bizzagi\\project\\key\\capstone-424305-ac71adf52988.json"

    # Ensure destination directory exists
    if destination_directory and not os.path.exists(destination_directory):
        os.makedirs(destination_directory)

    storage_client = Client()
    bucket = storage_client.bucket(bucket_name)

    blob_names = [blob.name for blob in bucket.list_blobs(max_results=max_results)]

    results = transfer_manager.download_many_to_path(
        bucket, blob_names, destination_directory=destination_directory, max_workers=workers
    )

    for name, result in zip(blob_names, results):
        if isinstance(result, Exception):
            print(f"Failed to download {name} due to exception: {result}")
        else:
            print(f"Downloaded {name} to {os.path.join(destination_directory, name)}")

if __name__ == "__main__":
    bucket_name = "namer-model-bucket"
    destination_directory = "last-model"
    download_bucket_with_transfer_manager(bucket_name, destination_directory)
