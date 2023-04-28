import json
import boto3
import time
import os
import uuid

def get_business_name(event):
    audio_filename = event['detail']['object']['key']
    stopKey = audio_filename.replace('/', '|', 1).find('/')
    startKey = audio_filename.find('/')
    return audio_filename[startKey+1: stopKey]

def lambda_handler(event, context):

    transcribe = boto3.client(service_name='transcribe', region_name='us-east-1')
    audio_filename = event['detail']['object']['key']
    bucket = event['detail']['bucket']['name']
    transcribe_output_prefix = 'transcribe-output/'
    audiofile_loc = 's3://{}/{}'.format(bucket, audio_filename)
    business_name = get_business_name(event)
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
        'bucket_name': bucket,
        'business_name': business_name
        }
    

    return output
