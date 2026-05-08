# Lambda: speech_to_text
# Triggered by an HTTP request. Reads a user's .flac audio file from S3,
# submits it to AWS Transcribe, polls until complete, then publishes the
# transcript to an SQS queue for downstream processing.

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
QUEUE_URL = os.environ.get('SQS_QUEUE_URL')

#TODO modify to be triggered by a flac file upload to bucket 

def handler(event: dict, context):
    """Lambda entry point. Transcribes the user's audio file and publishes the result to SQS.

    Args:
        event: The Lambda event dict. Expected to contain 'queryStringParameters'
               with a 'user' key identifying whose audio file to process.
        context: The Lambda context object (unused).

    Returns:
        A dict with 'statusCode' 200 and a JSON body containing 'jobId' and 'transcription'.
    """
    logger.info(f"LOCAL_TEST: {LOCAL_TEST}")
    logger.info(f"S3_BUCKET: {S3_BUCKET}")
    logger.info(f"Event: {event}")
    
    # extract the user identifier from the query string
    query_parameters: dict = event.get('queryStringParameters')
    user = query_parameters.get("user")
    # transcribe the user's audio file stored in S3
    transcribe = Transcribe(bucket=S3_BUCKET, user=user)
    transcription = transcribe.transcribe()
    job_id = str(uuid.uuid4())

    # publish the transcript to SQS so the response Lambda can pick it up
    if LOCAL_TEST != None:
        sqs.send_message(
            QueueUrl=QUEUE_URL,
            MessageBody=json.dumps({
                "jobId": job_id,
                "user": user,
                "transcription": transcription}))
        
    return {
        'statusCode': 200,
        'body': json.dumps({
            "jobId": job_id,
            "transcription": transcription})
    }


class Transcribe:
    def __init__(self, bucket, user):
        """Initialise a Transcribe job for the given user's audio file.

        Args:
            bucket: The S3 bucket name where audio uploads and transcripts are stored.
            user: The user identifier; the audio file is expected at uploads/<user>.flac.
        """
        # derive the S3 key from the user's name — expects uploads/<user>.flac
        self.bucket = bucket
        self.key = f"uploads/{user}.flac"
        self.user = user

    def start_transcription(self) -> str:
        """Submit a new AWS Transcribe job for the user's audio file.

        Returns:
            The unique transcription job name that can be used to poll for results.
        """
        job_name = f"job-{uuid.uuid4()}"  # must be unique

        # submit the audio file to AWS Transcribe and return the job name
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
                # parse the S3 URI to locate the output transcript file
                bucket = job['Transcript']['TranscriptFileUri'].split('/')[3]
                s3_key = '/'.join(job['Transcript']['TranscriptFileUri'].split('/')[4:])
                obj = s3.get_object(Bucket=bucket, Key=s3_key)
                transcript_data = json.loads(obj['Body'].read().decode())
                return transcript_data['results']['transcripts'][0]['transcript']

            if status == 'FAILED':
                reason = job.get('FailureReason', 'Unknown')
                raise RuntimeError(f"Transcription job failed: {reason}")

    def transcribe(self):
        """Start a transcription job and block until the transcript is returned.

        Returns:
            The transcript text as a string.
        """
        # orchestrate: start the job then wait for the result
        job_name = self.start_transcription()
        return self.get_transcription(job_name)
