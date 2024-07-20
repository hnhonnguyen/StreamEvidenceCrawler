import io
from minio import Minio
from dotenv import load_dotenv
import os
import sys

class ImageProcessor:
    def __init__(self) -> None:
        self.minio_client = self.__init_minio_client()
    
    def __init_minio_client(self):
        load_dotenv()

        # Fetching the environment variables
        minio_access_key = os.getenv('MINIO_ROOT_USER')
        minio_secret_key = os.getenv('MINIO_ROOT_PASSWORD')
        minio_endpoint = os.getenv('MINIO_ENDPOINT')
        return Minio(
            minio_endpoint,
            access_key=minio_access_key,
            secret_key=minio_secret_key,
            secure=False)

    def check_bucket_exist(self, bucket_name) -> bool:
        return self.minio_client.bucket_exists(bucket_name)

    def create_bucket(self, bucket_name):
        self.minio_client.make_bucket(bucket_name)

    def upload_file_image(self, bucket_name, object_name, file_path):
        self.minio_client.fput_object(
            bucket_name, object_name, file_path=file_path
        )

    def upload_binary_image(self, bucket_name, object_name, data):
        buf = io.BytesIO(data)
        buf_length = buf.getbuffer().nbytes
        
        if not self.check_bucket_exist(bucket_name):
            self.create_bucket(bucket_name)
            
        return self.minio_client.put_object(
            bucket_name, object_name, buf, buf_length, content_type='image/png'
            )

    def get_image(self, bucket_name, object_name):
        try:
            data = self.minio_client.get_object(bucket_name, object_name)
            return data.read()
        except Exception as err:
            print(err)
            return None
