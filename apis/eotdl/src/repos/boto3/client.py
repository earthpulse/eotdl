import boto3

# from botocore.client import Config
import os


# def get_session():
#     return Session(
#         aws_access_key_id=os.environ["ACCESS_KEY_ID"],
#         aws_secret_access_key=os.environ["SECRET_ACCESS_KEY"],
#         region_name=os.getenv("S3_REGION", "us-east-1"),
#     )


def get_client():
    HTTPS = os.getenv("S3_SSL", False)
    HTTP_PREFIX = "http://" if HTTPS else "https://"  # ???
    # print("HTTPS", HTTPS, HTTP_PREFIX)
    return boto3.client(
        "s3",
        aws_access_key_id=os.environ["ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["SECRET_ACCESS_KEY"],
        # region_name=os.getenv("S3_REGION", "us-east-1"),
        # use_ssl=os.getenv("S3_SSL", False),
        endpoint_url=HTTP_PREFIX + os.environ["S3_ENDPOINT"],
        # verify=False,
        # config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
        config=boto3.session.Config(signature_version="s3v4"),
    )
