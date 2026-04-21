import json
import boto3
import os
from mypy_boto3_sqs import SQSClient
import uuid

# set up logging
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# set up boto3 sdk
transcribe = boto3.client('transcribe')
s3 = boto3.client('s3')
sqs: SQSClient = boto3.client('sqs')

# set up env variables
LOCAL_TEST = os.environ.get('LOCAL_TEST', None)
S3_BUCKET = os.environ.get('S3_BUCKET', None)
logger.info(f"S3 bucket: {S3_BUCKET}")


def handler(event: dict, context):
    logger.info(f"Event: {event}")
    query_parameters: dict = event.get('queryStringParameters')
    user = query_parameters.get("user")
    transcribe = Transcribe(bucket=S3_BUCKET, user=user)
    transcription = transcribe.transcribe()

    if LOCAL_TEST != None:
        queue_url = os.environ['SQS_QUEUE_URL']
        sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps({
                "user": user,
                "transcription": transcription}))

    return {
        'statusCode': 200,
        'body': json.dumps(f"transcription: {transcription}")
    }


class Transcribe:
    def __init__(self, bucket, user):
        self.bucket = bucket
        self.key = f"uploads/{user}.flac"
        self.user = user

    def start_transcription(self) -> str:
        job_name = f"job-{uuid.uuid4()}"  # must be unique

        transcribe.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': f"s3://{self.bucket}/{self.key}"},
            MediaFormat='flac',
            LanguageCode='en-GB',
            OutputBucketName=self.bucket,
            OutputKey=f"transcripts/{job_name}.json"
        )

        return job_name

    def get_transcription(self, job_name: str) -> str:
        """Poll until the job completes and return the transcript text."""
        while True:
            response = transcribe.get_transcription_job(TranscriptionJobName=job_name)
            job = response['TranscriptionJob']
            status = job['TranscriptionJobStatus']

            if status == 'COMPLETED':
                bucket = job['Transcript']['TranscriptFileUri'].split('/')[3]
                s3_key = '/'.join(job['Transcript']['TranscriptFileUri'].split('/')[4:])
                obj = s3.get_object(Bucket=bucket, Key=s3_key)
                transcript_data = json.loads(obj['Body'].read().decode())
                return transcript_data['results']['transcripts'][0]['transcript']

            if status == 'FAILED':
                reason = job.get('FailureReason', 'Unknown')
                raise RuntimeError(f"Transcription job failed: {reason}")

    def transcribe(self):
        job_name = self.start_transcription()
        return self.get_transcription(job_name)
