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
LOCAL_TEST = os.environ.get('LOCAL_TEST', None)

def handler(event, context):
    logger.info(f"Event: {event}")
    # get the message out of the SQS event
    message = event['Records'][0]['body']
    data: dict = json.loads(message)
    # write event data to DDB table
    user = data.get('user')
    transcript = data.get('transcription')
    response = generate_response(transcript)

    if LOCAL_TEST != None:
        TABLENAME = os.environ['TABLE_NAME']
        dynamo.put_item(
            TableName=TABLENAME,
            Item={
                'id': {'S': str(uuid.uuid4())},
                'timestamp': {'S': datetime.datetime.now().isoformat()},
                'transcript': {'S': str(transcript)},
                'response': {'S': str(response)}
            }
        )
    else:
        return { "response": response }

def generate_response(prompt: str):
    client: BedrockRuntimeClient = boto3.client("bedrock-runtime", region_name="eu-west-2")  

    response = client.converse( 
        modelId="global.amazon.nova-2-lite-v1:0", 
        messages=[ 
            { 
                "role": "user", 
                "content": [{"text": prompt}]
            } 
        ] 
    )  

    return response["output"]["message"]["content"][0]["text"]