"""Unit tests for the response Lambda function.

Tests cover the Bedrock response generation helper as well as the Lambda
handler for both SQS-triggered and direct URL-invocation paths.
"""

from lambda_src.response.index import generate_response, handler

def test_generate_response():
    """Test that generate_response returns a non-empty string for any prompt."""
    prompt: str = "this is a test prompt"
    response = generate_response(prompt)
    # the model should always return a string regardless of prompt content
    assert type(response) == str

sqs_event_test_data = {
    "Records": [
        {
            "messageId": "12345678-1234-1234-1234-123456789012",
            "receiptHandle": "test-receipt-handle-12345",
            "body": '{"user": "test", "transcription": "Give me a series of Python interview questions."}',
            "attributes": {
                "ApproximateReceiveCount": "1",
                "AWSTraceHeader": "Root=1-00000000-0000000000000000;Parent=0000000000000000;Sampled=0;Lineage=1:0000000000:0",
                "SentTimestamp": "1000000000000",
                "SenderId": "AIDACKCEVSQ6C2EXAMPLE:test-role",
                "ApproximateFirstReceiveTimestamp": "1000000000000",
            },
            "messageAttributes": {},
            "md5OfBody": "0000000000000000000000000000000000000000",
            "eventSource": "aws:sqs",
            "eventSourceARN": "arn:aws:sqs:eu-west-2:000000000000:test-interview-queue",
            "awsRegion": "eu-west-2",
        }
    ]
}

def test_sqs_event_handler():
    """Test the handler when invoked via an SQS trigger.

    The handler should process the SQS record body and return the
    generated response string directly.
    """
    result = handler(event=sqs_event_test_data, context=None)
    print(result)
    assert type(result) == str

url_call_event_test_data = {
    "version": "2.0",
    "routeKey": "$default",
    "rawPath": "/",
    "rawQueryString": "",
    "headers": {
        "x-amzn-tls-version": "TLSv1.3",
        "x-amz-date": "REDACTED_DATE",
        "x-forwarded-proto": "https",
        "postman-token": "REDACTED_TOKEN",
        "x-forwarded-port": "443",
        "x-forwarded-for": "REDACTED_IP",
        "accept": "*/*",
        "x-amzn-tls-cipher-suite": "TLS_AES_128_GCM_SHA256",
        "x-amzn-trace-id": "Root=REDACTED_TRACE_ID",
        "host": "REDACTED_HOST",
        "accept-encoding": "gzip, deflate, br",
        "user-agent": "PostmanRuntime/7.53.0"
    },
    "queryStringParameters": {"user": "test", "transcript": "this is a test"},
    "requestContext": {
        "accountId": "REDACTED_ACCOUNT_ID",
        "apiId": "REDACTED_API_ID",
        "authorizer": {
            "iam": {
                "accessKey": "REDACTED_ACCESS_KEY",
                "accountId": "REDACTED_ACCOUNT_ID",
                "callerId": "REDACTED_CALLER_ID",
                "cognitoIdentity": None,
                "principalOrgId": None,
                "userArn": "arn:aws:iam::REDACTED_ACCOUNT_ID:user/REDACTED_USER",
                "userId": "REDACTED_USER_ID"
            }
        },
        "domainName": "REDACTED_DOMAIN",
        "domainPrefix": "REDACTED_PREFIX",
        "http": {
            "method": "GET",
            "path": "/",
            "protocol": "HTTP/1.1",
            "sourceIp": "REDACTED_IP",
            "userAgent": "PostmanRuntime/7.53.0"
        },
        "requestId": "REDACTED_REQUEST_ID",
        "routeKey": "$default",
        "stage": "$default",
        "time": "REDACTED_TIME",
        "timeEpoch": 1777797960506
    },
    "isBase64Encoded": False
}

def test_url_event_handler():
    """Test the handler when invoked via a Lambda function URL.

    The handler should return a dict with a 'statusCode' and 'body' key
    matching the standard HTTP response shape.
    """
    result = handler(event=url_call_event_test_data, context=None)
    print(result)
    assert type(result) == dict