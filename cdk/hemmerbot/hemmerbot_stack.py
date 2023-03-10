import os
from os.path import dirname

import aws_cdk.aws_logs
from aws_cdk import (
    # Duration,
    Stack,
    RemovalPolicy,
    aws_s3 as s3,
    aws_lambda as lambda_,
)
from constructs import Construct
from aws_cdk.aws_events import Rule
from aws_cdk.aws_events import Schedule
import aws_cdk.aws_events_targets as targets
from aws_cdk import Duration

# ARN of the S3 bucket to store application data
S3_BUCKET_ARN = "arn:aws:s3:::skm-trend-replicator"
S3_BUCKET_NAME = "skm-trend-replicator"

class HemmerbotStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        # example resource
        bucket = s3.Bucket.from_bucket_arn(self,
                                           "ImportedBucket",
                                           bucket_arn=S3_BUCKET_ARN)

        runtime_environment_layer = lambda_.LayerVersion(self, "Runtime",
                                                         removal_policy=RemovalPolicy.DESTROY,
                                                         compatible_runtimes=[lambda_.Runtime.PYTHON_3_9],
                                                         code=lambda_.Code.from_asset(os.path.abspath(
                                                             os.path.join(dirname(__file__), '..', '..', 'shared-layer'))),
                                                         compatible_architectures=[lambda_.Architecture.ARM_64])

        # Lambda scripts
        trend_replicator = lambda_.Function(self,
                                            "TrendReplicator",
                                            runtime=lambda_.Runtime.PYTHON_3_9,
                                            handler="trending_statuses.lambda_handler",
                                            code=lambda_.Code.from_asset(os.path.abspath(
                                                os.path.join(dirname(__file__), '..', '..', 'lambda-functions', 'hemmerbot'))),
                                            layers=[runtime_environment_layer],
                                            log_retention=aws_cdk.aws_logs.RetentionDays.ONE_DAY,
                                            environment={
                                                "S3_BUCKET_NAME": S3_BUCKET_NAME
                                            },
                                            timeout=Duration.minutes(1)
                                            )
        hashtag_replicator = lambda_.Function(self,
                                            "HashtagReplicator",
                                            runtime=lambda_.Runtime.PYTHON_3_9,
                                            handler="followed_hashtags.lambda_handler",
                                            code=lambda_.Code.from_asset(os.path.abspath(
                                                os.path.join(dirname(__file__), '..', '..', 'lambda-functions', 'hemmerbot'))),
                                            layers=[runtime_environment_layer],
                                            log_retention=aws_cdk.aws_logs.RetentionDays.ONE_DAY,
                                            environment={
                                                "S3_BUCKET_NAME": S3_BUCKET_NAME
                                            },
                                            timeout=Duration.minutes(1)
                                            )
        bucket.grant_read_write(trend_replicator)
        bucket.grant_read_write(hashtag_replicator)

        # Periodic invocation
        rule_trend_replicator = Rule(self,
                    "PeriodicTrendReplicatorEvents",
                    schedule=Schedule.rate(duration=Duration.minutes(20)),
                    targets=[targets.LambdaFunction(trend_replicator)])

        rule_hashtag_replicator = Rule(self,
                    "PeriodicHashtagReplicatorEvents",
                    schedule=Schedule.rate(duration=Duration.minutes(20)),
                    targets=[targets.LambdaFunction(hashtag_replicator)])
