from minio import Minio
import os

client = {}

def get_client():
    if not 'minio' in client:
        if 'S3_REGION' in os.environ:
            client['minio'] = Minio(
                endpoint=os.environ['S3_ENDPOINT'],
                access_key=os.environ['ACCESS_KEY_ID'],
                secret_key=os.environ['SECRET_ACCESS_KEY'],
                secure=True,
                region=os.environ['S3_REGION'],
            )
        else:
            client['minio'] = Minio(
                endpoint=os.environ['S3_ENDPOINT'],
                access_key=os.environ['ACCESS_KEY_ID'],
                secret_key=os.environ['SECRET_ACCESS_KEY'],
                secure=False
            )
    return client['minio']
