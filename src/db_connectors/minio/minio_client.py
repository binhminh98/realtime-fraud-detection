"""
Helper module to connect to MinIO and perform operations like uploading files.
"""

import os
from io import BytesIO
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from minio import Minio

from src.general_utils.logging import get_logger

load_dotenv(override=True)

file_logger = get_logger(
    "file_" + __name__,
    write_to_file=True,
    log_filepath=Path(r"logs/minio/minio_s3.log"),
)

stream_logger = get_logger(
    "stream_" + __name__,
)


class MinioClient:
    def __init__(self):
        """
        Initialize the MinIO client with the provided MinIO client instance.
        """
        self.minio_client = self._init_client()

    def _init_client(self):
        """
        Initialize the MinIO client with the necessary configuration.
        """
        return Minio(
            endpoint=os.getenv("MINIO_ENDPOINT"),
            access_key=os.getenv("MINIO_ACCESS_KEY"),
            secret_key=os.getenv("MINIO_SECRET_KEY"),
            secure=False,  # Set to True if using HTTPS
        )

    def upload_file(self, bucket_name, destination_file_name, file_path):
        """
        Upload a file to the specified MinIO bucket.
        """
        if not self.minio_client.bucket_exists(bucket_name):
            self.minio_client.make_bucket(bucket_name)
            stream_logger.info(f"Bucket '{bucket_name}' created.")

        try:
            self.minio_client.fput_object(
                bucket_name, destination_file_name, file_path
            )
            stream_logger.info(
                f"File '{file_path}' uploaded to bucket '{bucket_name}' as '{destination_file_name}'."
            )
        except Exception as e:
            file_logger.error(f"Failed to upload file: {e}")
            stream_logger.error(f"Failed to upload file: {e}")

    def download_file(self, bucket_name, destination_file_name, file_path):
        """
        Download a file from the specified MinIO bucket.
        """
        try:
            self.minio_client.fget_object(
                bucket_name, destination_file_name, file_path
            )
            stream_logger.info(
                f"File '{destination_file_name}' downloaded from bucket '{bucket_name}' to '{file_path}'."
            )
        except Exception as e:
            file_logger.error(f"Failed to download file: {e}")
            stream_logger.error(f"Failed to download file: {e}")

    def list_files(self, bucket_name) -> list:
        """
        List all files in the specified MinIO bucket.
        """
        try:
            objects = self.minio_client.list_objects(
                bucket_name, recursive=True
            )
            file_list = [obj.object_name for obj in objects]
            stream_logger.info(f"Files in bucket '{bucket_name}': {file_list}")
            return file_list
        except Exception as e:
            file_logger.error(f"Failed to list files: {e}")
            stream_logger.error(f"Failed to list files: {e}")
            return []

    def delete_file(self, bucket_name, file_name):
        """
        Delete a file from the specified MinIO bucket.
        """
        try:
            self.minio_client.remove_object(bucket_name, file_name)
            stream_logger.info(
                f"File '{file_name}' deleted from bucket '{bucket_name}'."
            )
        except Exception as e:
            file_logger.error(f"Failed to delete file: {e}")
            stream_logger.error(f"Failed to delete file: {e}")

    def delete_bucket(self, bucket_name):
        """
        Delete the specified MinIO bucket.
        """
        try:
            self.minio_client.remove_bucket(bucket_name)
            stream_logger.info(f"Bucket '{bucket_name}' deleted.")
        except Exception as e:
            file_logger.error(f"Failed to delete bucket: {e}")
            stream_logger.error(f"Failed to delete bucket: {e}")

    def get_csv_data(self, bucket_name, file_name) -> pd.DataFrame | None:
        """
        Get CSV data from the specified MinIO bucket.
        """
        if ".csv" not in file_name:
            raise Exception(
                f"File '{file_name}' is not a CSV file. Please provide a valid CSV file."
            )

        try:
            response = self.minio_client.get_object(bucket_name, file_name)

            # For large files
            chunk_size = 40960
            csv_bytes = b''.join(response.stream(chunk_size))
            csv_buffer = BytesIO(csv_bytes)

            stream_logger.info(
                f"CSV data retrieved from '{file_name}' in bucket '{bucket_name}'."
            )

            response.close()
            response.release_conn()

            return pd.read_csv(csv_buffer)
        except Exception as e:
            file_logger.error(f"Failed to get CSV data: {e}")
            stream_logger.error(f"Failed to get CSV data: {e}")
            return None

    def get_file_buffer_as_bytes(self, bucket_name, file_name) -> BytesIO | None:
        """
        Get a file from the specified MinIO bucket as a BytesIO object.
        """
        try:
            response = self.minio_client.get_object(bucket_name, file_name)
        
            # For large files
            chunk_size = 8192
            file_bytes = b''.join(response.stream(chunk_size))
            file_buffer = BytesIO(file_bytes)

            stream_logger.info(
                f"File '{file_name}' retrieved from bucket '{bucket_name}'."
            )

            response.close()
            response.release_conn()

            return file_buffer
        except Exception as e:
            file_logger.error(f"Failed to get file buffer: {e}")
            stream_logger.error(f"Failed to get file buffer: {e}")

            return None

if __name__ == "__main__":
    # import kagglehub

    # file_path = kagglehub.dataset_download("mlg-ulb/creditcardfraud")
    # dir_list = os.listdir(file_path)

    minio_client = MinioClient()
    bucket_name = "fraudetection"

    # # Upload a file
    # for file_name in dir_list:
    #     full_file_path = os.path.join(file_path, file_name)
    #     minio_client.upload_file(bucket_name, file_name, full_file_path)

    # # Download a file
    # minio_client.download_file(
    #     bucket_name,
    #     "creditcard.csv",
    #     Path("data/creditcard.csv"),
    # )

    # Delete a bucket
    minio_client.delete_bucket(bucket_name)
