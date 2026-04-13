import json
import os

def handler(event, context):
    body: dict = json.loads(event['Records'][0]['body'])
    user = body.get('user')
    transcription = body.get('transcription')
    print(f"{user} {transcription}")
    return