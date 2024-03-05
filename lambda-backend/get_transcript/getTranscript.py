import json
import boto3
import time
import os
import uuid

def lambda_handler(event, context):

    transcribe = boto3.client(service_name='transcribe', region_name='us-west-2')
    audio_filename = event['detail']['object']['key']
    bucket = event['detail']['bucket']['name']
    parts = audio_filename.split('/')
    business_name = parts[1]
    
    # storing filename in Unix time will allow us to retrieve objects after a certain point for later file merging
    transcript_filename = int(time.time())
    transcribe_output_prefix = 'transcribe-output/{}/{}.json'.format(business_name, transcript_filename)
    
    # If there are 4 parts to the key then we have an event name also
    if len(parts) == 5:
        event_name = parts[3]
        transcribe_output_prefix = 'transcribe-output/{}/events/{}/{}.json'.format(business_name, event_name, transcript_filename)
    
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
        'bucket_name': bucket,
        'business_name': business_name
        }
    

    return output
