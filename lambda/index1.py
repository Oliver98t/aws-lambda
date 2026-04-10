import json
import os

def handler(event, context):
    # Get environment variables
    environment = os.environ.get('ENVIRONMENT', 'unknown')
    
    # Build response
    response_body = {
        "message": "Hello from index2",
        "environment": environment,
        "path": event.get('rawPath', '/'),
        "method": event.get('requestContext', {}).get('http', {}).get('method', 'UNKNOWN')
    }
    
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(response_body)
    }