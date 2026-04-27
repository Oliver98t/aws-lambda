import boto3
import datetime
import os
import json
import uuid
from mypy_boto3_bedrock_runtime import BedrockRuntimeClient

import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# create the DynamoDB resource
dynamo = boto3.client('dynamodb')

def handler(event, context):
    logger.info(f"Event: {event}")

    return {
        'statusCode': 200,
        'body': "testing"
    }
    