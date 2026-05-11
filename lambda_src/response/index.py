# Lambda: response
# Triggered by SQS messages or direct URL invocations.
# Calls Amazon Bedrock to generate an AI response for a given transcript,
# then persists the result to DynamoDB.

import boto3
import datetime
import os
import json
import uuid
from mypy_boto3_dynamodb import DynamoDBServiceResource
from mypy_boto3_bedrock_runtime import BedrockRuntimeClient

import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

ddb_resource: DynamoDBServiceResource = boto3.resource('dynamodb')
LOCAL_TEST = os.environ.get('LOCAL_TEST', None)
TABLENAME = os.environ.get('TABLE_NAME')

def handler(event, context):
    """Lambda entry point. Routes to the correct handler based on the event source.

    Args:
        event: The Lambda event dict. Contains 'Records' for SQS triggers
               or 'version' for Lambda function URL invocations.
        context: The Lambda context object (unused).

    Returns:
        The result from either sqs_event() or url_event().
    """
    logger.info(f"LOCAL_TEST: {LOCAL_TEST}")
    logger.info(f"Event: {event}")

    # Route to the appropriate handler based on the event source
    if event.get('Records'):
        logger.info("SQS trigger")
        data = sqs_event(event)
    elif event.get('version'):
        logger.info("url trigger")
        data = url_event(event)

    return data

def sqs_event(event):
    """Handle an SQS-triggered invocation.

    Parses the SQS message body, generates a Bedrock response for the
    transcript, and writes the result to DynamoDB.

    Args:
        event: The raw SQS event dict containing a 'Records' list.

    Returns:
        The generated AI response string.
    """
    # get the message out of the SQS event
    message = event['Records'][0]['body']
    data: dict = json.loads(message)
    # extract fields from the SQS message payload
    job_id = data.get('jobId')
    user_name = data.get('user_name')
    transcript = data.get('transcription')
    # generate an AI response for the transcript
    response = generate_response(prompt=transcript, user_name=user_name)

    # write event data to DDB table
    result = write_to_db({"user": user_name, 
                          "transcript": transcript,
                          "response": response, 
                          "job_id": job_id})
    return result

def url_event(event) -> dict:
    """Handle a direct HTTP invocation via Lambda function URL or API Gateway.

    Reads 'user' and 'transcript' from the query string, generates a Bedrock
    response, persists it to DynamoDB, and returns an HTTP response dict.

    Args:
        event: The Lambda event dict containing 'queryStringParameters'.

    Returns:
        A dict with 'statusCode' (200 or 500) and a JSON 'body'.
    """
    # Handle a direct HTTP invocation via URL function URL or API Gateway
    try:
        query_parameters: dict = event.get('queryStringParameters')
        job_id = str(uuid.uuid4())
        user_name = query_parameters.get("user_name")
        transcript = query_parameters.get("transcript")
        # generate an AI response for the provided transcript

        response = generate_response(prompt=transcript, user_name=user_name)

        write_to_db({"user_name":   user_name, 
                    "transcript":   transcript,
                    "response":     response, 
                    "job_id":       job_id})
        
        status_code = 200
        body = json.dumps({"jobId": job_id, "response": response})
    except Exception as e:
        logger.error(f"Exception: {e}")
        status_code = 500
        body = None
    return {
        'statusCode': status_code,
        'body': body
    }

def read_db(user_value: str):
    response = None
    try:
        table = ddb_resource.Table(TABLENAME)
        response = table.scan(
            FilterExpression=boto3.dynamodb.conditions.Attr('user_name').eq(user_value)
        )
        response.get('Items', [])
    except Exception as e:
        logger.error(f"Exception: {e}")

    return response

def write_to_db(data: dict):
    """Persist the response data to DynamoDB.

    Args:
        data: A dict containing 'job_id', 'user', 'transcript', and 'response'.

    Returns:
        The AI response string from data['response'].
    """
    result = data['response']
    # only write to DynamoDB when running in a live environment (not local tests)
    if LOCAL_TEST != None:
        logger.info("writing to dynamodb")
        table = ddb_resource.Table(TABLENAME)
        table.put_item(
            Item={
                'id':           str(data['job_id']),
                'user_name':    str(data['user_name']),
                'timestamp':    datetime.datetime.now().isoformat(),
                'transcript':   str(data['transcript']),
                'response':     str(data['response'])
            }
        )
    return result

# TODO create a history function
def create_message_history(history: dict)-> list:
    items = history.get('Items')
    items_num = len(items)
    message_history = []
    for item in items:
        response: dict = json.loads(item.get('response'))
        answer = response.get('answer')
        question = response.get('question')
        if answer != None and question != None:
            message_history.append(
                {
                    "role": "user",
                    "content": [{"text": response.get('answer')}]
                })
            message_history.append(
                {
                    "role": "assistant",
                    "content": [{"text": response.get('question')}]
                })
    return message_history

def generate_response(prompt: str, user_name: str):
    """Send a prompt to Amazon Bedrock and return the model's text response.

    Args:
        prompt: The input text (transcript) to send to the model.

    Returns:
        The generated response text as a string.
    """
    # Bedrock currently only supports the client API in boto3, not resource API.
    bedrock: BedrockRuntimeClient = boto3.client("bedrock-runtime", region_name="eu-west-2")
    history = read_db(user_value=user_name)
    message_history = create_message_history(history=history)
    messages = message_history
    logger.info(f"history {history}")
    messages.append({"role": "user",
                     "content": [{"text": prompt}]})
    logger.info(f"messages {messages}")
    # send the transcript to the model and retrieve the generated text
    response = bedrock.converse(
        modelId="global.amazon.nova-2-lite-v1:0",
        messages=messages
    )

    return response["output"]["message"]["content"][0]["text"]
