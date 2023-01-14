import json
import boto3
import os

def lambda_handler(event, context):
    
    comprehend = boto3.client(service_name='comprehend', region_name='us-east-1')
    s3 = boto3.client('s3')
    bucket = event['bucket_name']
    transcribe_output_prefix = 'transcribe-output'
    job_name = event['transcript_job_name']
    job_timestamp = event['interaction_date_time']
    business_name = event['business_name']
    
    # Opening JSON file
    key = '{}/{}/{}.json'.format(transcribe_output_prefix,business_name,job_name)
    data = s3.get_object(Bucket=bucket, Key=key)
    content = data['Body'].read().decode("utf-8")
    json_content = json.loads(content)
    text = json_content['results']['transcripts'][0]['transcript']

    # Detect sentiment
    sentiment = comprehend.detect_sentiment(Text=text, LanguageCode='en')
    output = {
        'business_name': business_name,
        'transcript_job_name': job_name,
        'interaction_date_time': job_timestamp,
        'bucket_name': bucket,
        'sentiment': {
            'overallSentiment': sentiment['Sentiment']
            }
    }
    
    
    return output
