import json
import boto3
import uuid
import logging
import time
import tarfile
from io import BytesIO
from botocore.exceptions import ClientError
from decimal import Decimal

logger = logging.getLogger(__name__)
s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

def filteredSentiment(targeted_sentiment):
    objects = []
    object_sentiments = []
    for i in range(len(targeted_sentiment["Entities"])):
        for j in range(len(targeted_sentiment["Entities"][i]["Mentions"])):
            if targeted_sentiment["Entities"][i]["Mentions"][j]["Type"] in ["ATTRIBUTE", "OTHER"]:
                objects.append(targeted_sentiment["Entities"][i]["Mentions"][j]["Text"])
                object_sentiments.append(targeted_sentiment["Entities"][i]["Mentions"][j]["MentionSentiment"]["Sentiment"])
    return {objects[i]: object_sentiments[i] for i in range(len(objects))}

def recordSentiment(interaction_id, business_name, sentiment):
    interactionsTbl = dynamodb.Table('interactions')
    try:
        interactionsTbl.put_item(
            Item={
                'interaction_id': interaction_id,
                'date_time': Decimal(time.time()),
                'business_name': business_name,
                'overall_sentiment': sentiment
            }
        )
    except ClientError as err:
        logger.error(
            "Couldn't add interaction to table %s. Here's why: %s: %s",
            'interactions',
            err.response['Error']['Code'], err.response['Error']['Message'])
        raise
    
    return 'success'

def recordTargetedSentiment(interaction_id, object_name, sentiment):
    targetedSentimentTbl = dynamodb.Table('Targeted_sentiment')
    try:
        targetedSentimentTbl.put_item(
            Item={
                'interaction_id': interaction_id,
                'object_name': object_name,
                'sentiment': sentiment
            }
        )
    except ClientError as err:
        logger.error(
            "Couldn't add interaction to table %s. Here's why: %s: %s",
            'interactions',
            err.response['Error']['Code'], err.response['Error']['Message'])
        raise
    
    return 'success'
    
def read_and_process_batchfile(interaction_id, business_name, content, file_type):
    # we'll read the uncompressed file line by line and record into DynamoDB
    tar = tarfile.open(fileobj = BytesIO(content))
    for member in tar.getmembers():
         f = tar.extractfile(member)
         if f is not None:
            while True:
                line = f.readline().decode("utf-8")
                if not line:
                    break
                if file_type == 'targeted_sentiment':
                    x = filteredSentiment(json.loads(line))
                    for key in x:
                        recordTargetedSentiment(interaction_id, key, x[key])
                elif file_type == 'overall_sentiment':
                    x = json.loads(line)
                    recordSentiment(interaction_id, business_name, x["Sentiment"])
                else:
                    raise "invalid file type"
    return 'success'

def lambda_handler(event, context):
    
    GUID = uuid.uuid1().int>>64 # this is our interaction_id
    bucket = 'nlp-feedback-app'
    business_name = event['business_name']
    batch_output_prefix = 'batch/output/{}/output'.format(business_name)     
    
    # Let's open Overall Sentiment compressed file
    overall_sentiment_job = event['overall_sentiment_job_name']
    key = '{}/{}/output/output.tar.gz'.format(batch_output_prefix, overall_sentiment_job)
    data = s3.get_object(Bucket=bucket, Key=key)
    content = data['Body'].read()
    read_and_process_batchfile(GUID, business_name, content, 'overall_sentiment');

    
    # Let's open Targeted Sentiment compressed file. Each line in targeted sentiment correspond to each line 
    # of overlal sentiment in the right order
    targeted_sentiment_job = event['targeted_sentiment_job_name']
    key = '{}/{}/output/output.tar.gz'.format(batch_output_prefix, targeted_sentiment_job)
    data = s3.get_object(Bucket=bucket, Key=key)
    content = data['Body'].read()
    read_and_process_batchfile(GUID, business_name, content, 'targeted_sentiment');
        
    return {
        'statusCode': 200,
        'body': json.dumps('Success')
    }

