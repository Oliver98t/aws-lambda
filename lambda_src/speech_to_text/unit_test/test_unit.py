"""Unit tests for the speech_to_text Lambda function.

These tests call AWS Transcribe and require valid AWS credentials and a
pre-uploaded test audio file at s3://ainterviewupload/uploads/test.flac.
"""

import lambda_src.speech_to_text.index as stt
from lambda_src.speech_to_text.index import Transcribe, handler
import json

def test_transcribe():
    """Test that the Transcribe class submits a job and returns the expected transcript."""
    transcribe = Transcribe(bucket="ainterviewupload", user="test")
    transcription = transcribe.transcribe()
    # expected transcript text from the test audio file
    test_trasncription = "Give me a series of Python interview questions."
    assert transcription == test_trasncription

event_test_data = {
    "version": "2.0",
    "routeKey": "$default",
    "rawPath": "/",
    "rawQueryString": "user=test",
    "headers": {
        "x-amzn-tls-version": "TLSv1.3",
        "x-amz-date": "20260420T122125Z",
        "x-forwarded-proto": "https",
        "postman-token": "test-token-12345",
        "x-forwarded-port": "443",
        "x-forwarded-for": "127.0.0.1",
        "accept": "*/*",
        "x-amzn-tls-cipher-suite": "TLS_AES_128_GCM_SHA256",
        "x-amzn-trace-id": "Root=1-00000000-0000000000000000",
        "host": "test-lambda-id.lambda-url.eu-west-2.on.aws",
        "cache-control": "no-cache",
        "accept-encoding": "gzip, deflate, br",
        "user-agent": "test-client/1.0",
    },
    "queryStringParameters": {"user": "test"},
    "requestContext": {
        "accountId": "000000000000",
        "apiId": "testlambdaid",
        "authorizer": {
            "iam": {
                "accessKey": "AKIAIOSFODNN7EXAMPLE",
                "accountId": "000000000000",
                "callerId": "AIDAEXAMPLE",
                "cognitoIdentity": None,
                "principalOrgId": None,
                "userArn": "arn:aws:iam::000000000000:user/test-user",
                "userId": "AIDAEXAMPLE",
            }
        },
        "domainName": "test-lambda-id.lambda-url.eu-west-2.on.aws",
        "domainPrefix": "testlambdaid",
        "http": {
            "method": "GET",
            "path": "/",
            "protocol": "HTTP/1.1",
            "sourceIp": "127.0.0.1",
            "userAgent": "test-client/1.0",
        },
        "requestId": "00000000-0000-0000-0000-000000000000",
        "routeKey": "$default",
        "stage": "$default",
        "time": "20/Apr/2026:12:21:25 +0000",
        "timeEpoch": 1000000000000,
    },
    "isBase64Encoded": False,
}

def test_handler(monkeypatch):
    """Test the Lambda handler end-to-end with a realistic URL-invocation event.

    Monkeypatches S3_BUCKET so the handler targets the real test bucket without
    relying on environment variables being set locally.
    """
    monkeypatch.setattr(stt, "S3_BUCKET", "ainterviewupload")
    result = handler(event=event_test_data, context=None)
    body = json.loads(result['body'])
    # verify the HTTP response shape and transcript content
    assert result['statusCode'] == 200
    assert body['transcription'] == "Give me a series of Python interview questions."
