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
TABLENAME = os.environ.get('TABLE_NAME')

def handler(event, context):
    logger.info(f"LOCAL_TEST: {LOCAL_TEST}")
    logger.info(f"Event: {event}")

    if event.get('Records'):
        logger.info("SQS trigger")
        data = sqs_event(event)
    elif event.get('version'):
        logger.info("url trigger")
        data = url_event(event)

    return data

def sqs_event(event):
    # get the message out of the SQS event
    message = event['Records'][0]['body']
    data: dict = json.loads(message)
    # write event data to DDB table
    job_id = data.get('jobId')
    user = data.get('user')
    transcript = data.get('transcription')
    response = generate_response(transcript)

    result = write_to_db({"user": user, 
                          "transcript": transcript,
                          "response": response, 
                          "job_id": job_id})
    return result

def url_event(event) -> dict:
    try:
        query_parameters: dict = event.get('queryStringParameters')
        job_id = str(uuid.uuid4())
        user = query_parameters.get("user")
        transcript = query_parameters.get("transcript")
        response = generate_response(transcript)

        write_to_db({"user": user, 
                    "transcript": transcript,
                    "response": response, 
                    "job_id": job_id})
        
        status_code = 200
        body = json.dumps({"jobId": job_id, "response": response})
    except:
        status_code = 500
        body = None
    return {
        'statusCode': status_code,
        'body': body
    }

def write_to_db(data: dict):
    result = data['response']
    if LOCAL_TEST != None:
        logger.info("writing to dynamodb")
        dynamo.put_item(
            TableName=TABLENAME,
            Item={
                'id': {'S': str(data['job_id'])},
                'timestamp': {'S': datetime.datetime.now().isoformat()},
                'transcript': {'S': str(data['transcript'])},
                'response': {'S': str(data['response'])}
            }
        )
    return result

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
