import os
import requests
from requests_aws4auth import AWS4Auth

import subprocess


def get_lambda_function_url(function_name: str, region: str = "eu-west-2") -> str:
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
    access_key = os.environ["AWS_ACCESS_KEY_ID"]
    secret_key = os.environ["AWS_SECRET_ACCESS_KEY"]
    region = "eu-west-2"
    service = "lambda"

    auth = AWS4Auth(
        access_key,
        secret_key,
        region,
        service,
    )

    url = get_lambda_function_url("SpeechToText_dev")
    params = {"user": "test"}
    response = requests.get(url, params=params, auth=auth)
    assert response.status_code == 200
