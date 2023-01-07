import json
import boto3
import time
import os
import uuid

def lambda_handler(event, context):

    transcribe = boto3.client(service_name='transcribe', region_name='us-east-1')
    audio_filename = event['detail']['object']['key']
    bucket = event['detail']['bucket']['name']
    transcribe_output_prefix = 'transcribe-output/'
    audiofile_loc = 's3://{}/{}'.format(bucket, audio_filename)
    print('Calling StartTranscribe')
    job_name = str(uuid.uuid1())
    
    response = transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        LanguageCode='en-GB',
        MediaFormat='mp3',
        Media={
            'MediaFileUri': audiofile_loc
        },
        OutputBucketName=bucket,
        OutputKey=transcribe_output_prefix
    )
    
    output = {
        'transcript_job_name': response['TranscriptionJob']['TranscriptionJobName'],
        'job_status': response['TranscriptionJob']['TranscriptionJobStatus'],
        'interaction_date_time': str(time.time()),
        'bucket_name': bucket
        }
    

    return output
