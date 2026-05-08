"""Integration tests for the deployed AInterview backend Lambdas.

These tests make real HTTP calls to deployed Lambda function URLs and
require AWS credentials to be set in the environment:
  - AWS_ACCESS_KEY_ID
  - AWS_SECRET_ACCESS_KEY

Run against a live AWS environment only — not in CI without credentials.
"""

import os
import requests
from requests_aws4auth import AWS4Auth
import subprocess

def get_lambda_function_url(function_name: str, region: str = "eu-west-2") -> str:
    """Retrieve the function URL for a deployed Lambda using the AWS CLI.

    Args:
        function_name: The name of the Lambda function.
        region: The AWS region the function is deployed in.

    Returns:
        The HTTPS function URL as a string.
    """
    result = subprocess.run(
        [
            "aws",
            "lambda",
            "get-function-url-config",
            "--function-name",
            function_name,
            "--region",
            region,
            "--query",
            "FunctionUrl",
            "--output",
            "text",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()

def test_speech_to_text():
    """Integration test: invoke the deployed speech_to_text Lambda and verify a 200 response.

    Signs the request with AWS SigV4 credentials read from the environment,
    then calls the function URL with a 'user=test' query parameter.
    """
    # read AWS credentials from the environment
    access_key = os.environ["AWS_ACCESS_KEY_ID"]
    secret_key = os.environ["AWS_SECRET_ACCESS_KEY"]
    region = "eu-west-2"
    service = "lambda"

    # build SigV4 auth for the Lambda function URL
    auth = AWS4Auth(
        access_key,
        secret_key,
        region,
        service,
    )

    # resolve the live function URL and invoke it
    url = get_lambda_function_url("speech_to_text_dev")
    params = {"user": "test"}
    response = requests.get(url, params=params, auth=auth)
    assert response.status_code == 200
