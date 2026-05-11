"""Unit tests for the response Lambda function.

Tests cover the Bedrock response generation helper as well as the Lambda
handler for both SQS-triggered and direct URL-invocation paths.
"""

from lambda_src.response.index import generate_response, handler, create_message_history

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


history = {"Items": [{'response': '{"question": "Explain how you would handle a situation where a Python script encounters a race condition in a multi-threaded application. What strategies would you use to debug and resolve the issue?", "answer": "Handling a race condition in a multi-threaded Python application involves identifying the problematic code sections and ensuring proper synchronization. Here’s a structured approach to debug and resolve the issue:\\n\\n### Debugging Steps:\\n\\n1. **Reproduce the Issue**:\\n   - Write test cases or simulations that can consistently reproduce the race condition. This helps in verifying the fix later.\\n\\n2. **Logging and Tracing**:\\n   - Add detailed logging around shared resources and critical sections. Use thread IDs and timestamps to track the execution flow.\\n   - Example:\\n     ```python\\n     import logging\\n     import threading\\n     logging.basicConfig(level=logging.INFO, format=\'%(asctime)s - %(threadName)s - %(message)s\')\\n     ```\\n\\n3. **Use Debugging Tools**:\\n   - Utilize tools like `pdb` (Python Debugger) or `faulthandler` to step through multi-threaded code.\\n   - For more advanced analysis, consider using `gdb` with Python support or profiling tools like `cProfile`.\\n\\n4. **Thread Sanitizers**:\\n   - If using CPython, consider enabling the `faulthandler` module or third-party tools like `py-spy` for tracing and monitoring.\\n\\n### Resolving the Race Condition:\\n\\n1. **Synchronization Primitives**:\\n   - Use locks (`threading.Lock`) to protect critical sections:\\n     ```python\\n     lock = threading.Lock()\\n\\n     def thread_function():\\n         global shared_resource\\n         with lock:\\n             shared_resource += 1\\n     ```\\n   - For more complex scenarios, consider `threading.RLock` (re-entrant lock) if nested locking is needed.\\n\\n2. **Atomic Operations**:\\n   - Use atomic operations where possible. For example, use `queue.Queue` for thread-safe communication between threads.\\n\\n3. **Thread-Local Storage**:\\n   - If the data doesn’t need to be shared, use `threading.local()` to store thread-specific data.\\n\\n4. **Barriers and Condition Variables**:\\n   - Use `threading.Barrier` to synchronize the execution of threads at specific points.\\n   - Use `threading.Condition` when threads need to wait for certain states or events.\\n\\n5. **Avoiding Shared State**:\\n   - Design the application to minimize shared state. Use message passing (e.g., with `queue.Queue`) instead of shared variables whenever possible.\\n\\n6. **Testing**:\\n   - After applying fixes, run stress tests and multi-threaded test suites to ensure the race condition no longer occurs. Use tools like `pytest` with thread-aware plugins if available.\\n\\n### Example Fix:\\n\\n```python\\nimport threading\\nimport time\\n\\nshared_counter = 0\\nlock = threading.Lock()\\n\\ndef increment_counter():\\n    global shared_counter\\n    for _ in range(100000):\\n        with lock:\\n            shared_counter += 1\\n\\nthreads = []\\nfor _ in range(2):\\n    t = threading.Thread(target=increment_counter)\\n    threads.append(t)\\n    t.start()\\n\\nfor t in threads:\\n    t.join()\\n\\nprint(f\'Final counter value: {shared_counter}\')\\n```\\n\\nBy following these strategies, you can effectively debug and resolve race conditions in multi-threaded Python applications, ensuring data consistency and thread safety."}', 'id': '2679ee9d-899c-43d2-8b13-a12c1cd154b8', 'transcript': 'give just an interview question and answer in a json object string like {question: , answer:} \n                    for a Python dev, give just the object string and nothing else no mark down etc', 'user_name': 'test', 'timestamp': '2026-05-10T16:18:07.942967'}, {'response': '{"score": 10, "reason": "The answer correctly identifies a key difference between lists and tuples in Python (mutability), which is accurate and relevant. However, it could be improved by providing a more complete explanation (e.g., lists are mutable, tuples are immutable; both are sequence types) and including example use cases as requested in the question. While the focus on mutability is correct, the omission of use cases reduces comprehensiveness. Still, the core distinction is valid, warranting full points for accuracy on the main point."}', 'id': 'cca8c556-0f00-4137-808f-f45411d28f4d', 'transcript': 'based on this question: Explain the difference between a list and a tuple in Python, and give an example use case for each.\n\n                           and this answer: list is mutable\n\n                           output a score out of 10 and reason on a json object in the format {score: , reason: }\n                           give just the object string and nothing else no mark down etc', 'user_name': 'test', 'timestamp': '2026-05-10T16:18:27.403280'}, {'response': '{"score": 3, "reason": "The answer \'debugger\' is overly simplistic and does not adequately address the complexity of handling race conditions in multi-threaded Python applications. While using a debugger is a valid part of the debugging process, it alone does not constitute a comprehensive strategy. A complete answer should include identification of race conditions, strategies such as using locks, atomic operations, or thread-safe data structures, tools like logging, unit tests, and possibly specialized libraries (e.g., `threading` module features). The answer lacks depth, specific techniques, and resolution strategies, making it insufficient for a professional-level question on concurrency debugging."}', 'id': '12418402-8b82-482a-98e4-59de0b1f3d9d', 'transcript': 'based on this question: Explain how you would handle a situation where a Python script encounters a race condition in a multi-threaded application. What strategies would you use to debug and resolve the issue?\n\n                           and this answer: debugger\n\n                           output a score out of 10 and reason on a json object in the format {score: , reason: }\n                           give just the object string and nothing else no mark down etc', 'user_name': 'test', 'timestamp': '2026-05-10T16:18:17.016041'}, {'response': '{"question": "Explain the difference between a list and a tuple in Python, and give an example use case for each.", "answer": "In Python, both lists and tuples are used to store collections of items, but they have key differences:\\n\\nLists:\\n- Mutable (can be changed after creation)\\n- Defined using square brackets `[]`\\n- Can add, remove, or modify elements\\n- Generally used when you need to modify the collection\\n\\nExample use case for lists: When building a shopping cart where items can be added or removed dynamically.\\n\\nTuples:\\n- Immutable (cannot be changed after creation)\\n- Defined using parentheses `()`\\n- Elements cannot be added, removed, or modified\\n- Generally used when you need to ensure data integrity or when passing data between components safely\\n\\nExample use case for tuples: Representing coordinates (x, y) where the values should not change, or returning multiple values from a function where immutability is desired."}', 'id': '2f1cc9b4-bd71-4fcb-aa12-54393f409f64', 'transcript': 'check the history and give just an interview question and answer in a json object string like {question: , answer:} \n                    for a Python dev, give just the object string and nothing else no mark down etc', 'user_name': 'test', 'timestamp': '2026-05-10T16:18:18.951123'}]}

def test_create_history():
    message_history = create_message_history(history)
    print(message_history)
    assert type(message_history) == list