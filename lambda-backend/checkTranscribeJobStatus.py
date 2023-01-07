import json
import boto3

def lambda_handler(event, context):
    
    transcribe = boto3.client(service_name='transcribe', region_name='us-east-1')

    job_name = event['transcript_job_name']
    job_timestamp = event['interaction_date_time']
    bucket_name = event['bucket_name']
    response = transcribe.get_transcription_job(
    TranscriptionJobName=job_name
)

    output = {
        'transcript_job_name': response['TranscriptionJob']['TranscriptionJobName'],
        'interaction_date_time': job_timestamp,
        'job_status': response['TranscriptionJob']['TranscriptionJobStatus'],
        'bucket_name': bucket_name
        }

    return output