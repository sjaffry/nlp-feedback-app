import json
import boto3
import os

def extractBusinessName(key):
    start_idx = key.find("/", key.find("/", 0, len(key))+1, len(key))
    end_idx = key.find("/", start_idx+1, len(key))
    return key[start_idx+1:end_idx]

def lambda_handler(event, context):
    comprehend = boto3.client(service_name='comprehend', region_name='us-east-1')
    s3 = boto3.client('s3')
    bucket = event['detail']['bucket']['name']
    business_name = extractBusinessName(event['detail']['object']['key'])
    input_file_name = event['detail']['object']['key']
    input_file_loc = 's3://{}/{}'.format(bucket, input_file_name)
    output_loc = 's3://{}/batch/output/{}/'.format(bucket, business_name)
    
    # Let's get the overall sentiments first
    sentiment_job = comprehend.start_sentiment_detection_job(
    InputDataConfig={
        'S3Uri': input_file_loc,
        'InputFormat': 'ONE_DOC_PER_LINE'
    },
    OutputDataConfig={
        'S3Uri': output_loc
    },
    DataAccessRoleArn=os.environ['ROLE_ARN'],
    JobName='{}-sentiments'.format(business_name),
    LanguageCode='en'
    )

    # Next get the targeted sentiments
    ts_job = comprehend.start_targeted_sentiment_detection_job(
    InputDataConfig={
        'S3Uri': input_file_loc,
        'InputFormat': 'ONE_DOC_PER_LINE'
    },
    OutputDataConfig={
        'S3Uri': output_loc
    },
    DataAccessRoleArn=os.environ['ROLE_ARN'],
    JobName='{}-tgt-sentiments'.format(business_name),
    LanguageCode='en'
    )    
    
    # TODO Need to send the correct job name in output that becomes part of the file key in S3.
    
    output = {
    'business_name': business_name,
    'sentiment_job_id': sentiment_job["JobId"],
    'ts_job_id': ts_job["JobId"],
    'bucket_name': bucket
    }
    
    return output
