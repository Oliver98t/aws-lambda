# TODO create modules for each lambda function
# TODO connect lambda functions via queue
# TODO create a way to test each lambda function locally
# TODO create a folder structure for each lambda 
import json
import boto3
import os
from mypy_boto3_sqs import SQSClient
import uuid

transcribe = boto3.client('transcribe')
s3 = boto3.client('s3')
sqs: SQSClient = boto3.client('sqs')

def handler(event: dict, context):
    '''
    query_parameters: dict = event.get('queryStringParameters')
    print(query_parameters)
    user = query_parameters.get("user")
    transcription = None
    status = "FAIL"
    if query_parameters and user:
        status = "SUCCESS"
        print(f"USER: {user}")
        transcribe = Transcribe(bucket="ainterviewupload", user="test")
        transcription = transcribe.transcribe()
        queue_url = os.environ['SQSQUEUE1_QUEUE_URL']
        sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps({
                "user": user,
                "transcription": transcription}))
    '''
    return {
        'statusCode': 200,
        'body': "test"#json.dumps(f"Message: {transcription}")
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
            OutputBucketName=self.bucket,          # where transcript JSON is saved
            OutputKey=f"transcripts/{job_name}.json"
        )

        return job_name
    
    def get_transcription(self,job_name: str) -> str:
        """Poll until the job completes and return the transcript text."""
        while True:
            response = transcribe.get_transcription_job(TranscriptionJobName=job_name)
            job = response['TranscriptionJob']
            status = job['TranscriptionJobStatus']

            if status == 'COMPLETED':
                # Reconstruct the S3 key from the output location set in start_transcription
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

if __name__ == "__main__":
    Transcribe(bucket="ainterviewupload", user="test").transcribe()