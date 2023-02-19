from aws_cdk import (
    # Duration,
    Stack,
    RemovalPolicy,
    aws_s3 as s3
)
from constructs import Construct


class HemmerbotStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        # example resource
        bucket = s3.Bucket(self, "MyFirstBucket", removal_policy=RemovalPolicy.DESTROY, auto_delete_objects=True)

