import json
import os

import boto3
from botocore.exceptions import ClientError

S3_BUCKET_NAME = os.environ['S3_BUCKET_NAME']
SECRETS_OBJECT = 'secrets.json'
SECRETS_FILE = '/tmp/secrets.json'


def get_secrets():
    s3 = boto3.client('s3')
    s3.download_file(S3_BUCKET_NAME, SECRETS_OBJECT, SECRETS_FILE)

    try:
        with open(SECRETS_FILE, 'r') as infile:
            return json.load(infile)
    except FileNotFoundError:
        return set()
