from LambdaSrc.Response.Index import generate_response, handler

def test_generate_response():
    prompt: str = "this is a test prompt"
    response = generate_response(prompt)
    assert type(response) == str

event_test_data = {
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

def test_handler():
    result = handler(event=event_test_data, context=None)
    assert type(result['response']) == str