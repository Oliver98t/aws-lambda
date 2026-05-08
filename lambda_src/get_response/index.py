# Lambda: get_response
# Handles HTTP requests to retrieve a previously generated AI response.
# Looks up the result in DynamoDB by jobId and returns it to the caller.

import boto3
import os
import json


import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# get env variables
LOCAL_TEST = os.environ.get('LOCAL_TEST', None)
DYNAMODB_TABLE = os.environ.get('DYNAMODB_TABLE', None)

# create the DynamoDB resource
dynamo = boto3.resource('dynamodb')
table = dynamo.Table(DYNAMODB_TABLE)

def handler(event, context):
    """Lambda entry point. Looks up a stored AI response in DynamoDB by jobId.

    Args:
        event: The Lambda event dict. Expected to contain 'queryStringParameters'
               with a 'jobId' key.
        context: The Lambda context object (unused).

    Returns:
        A dict with 'statusCode' 200 and a JSON body containing the stored 'response'.
    """
    logger.info(f"Event: {event}")
    # extract the jobId from the query string to use as the DynamoDB lookup key
    query_parameters: dict = event.get('queryStringParameters')
    jobId = query_parameters.get("jobId")
    logger.info(jobId)

    if LOCAL_TEST != None:
        # Get a single item by primary key
        response = table.get_item(
            Key={'id': jobId}
        )
        logger.info(response)
        # pull the stored AI response text out of the DynamoDB item
        item = response.get('Item')
        response = item.get('response')
        
    return {
        'statusCode': 200,
        'body': json.dumps({
            "response": response
        })
    }
    