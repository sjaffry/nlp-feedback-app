import json
import boto3
import logging
import uuid
from botocore.exceptions import ClientError
from decimal import Decimal

logger = logging.getLogger(__name__)

def get_secret():

    secret_name = "Apps/DocumentDB/nlp-feedback"
    region_name = "us-east-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
        SecretId=secret_name
    )
    except ClientError as e:
        raise e

    secret = get_secret_value_response['SecretString']

    return json.loads(secret)

def lambda_handler(event, context):

    # remove garbage from input event
    businessName = event['business_name']
    interactionTimestamp = event['interaction_date_time']
    overallSentiment = event['sentiment']['overallSentiment']
    targetedSentiment = event['sentiment']['targetedSentiment']['Payload']
    
    
    # Interact with DB
    dynamodb = boto3.resource('dynamodb')
    interactionsTbl = dynamodb.Table('interactions')
    targetedSentimentTbl = dynamodb.Table('Targeted_sentiment')
    GUID = uuid.uuid1().int>>64


    try:
        interactionsTbl.put_item(
            Item={
                'interaction_id': GUID,
                'date_time': Decimal(interactionTimestamp),
                'business_name': businessName,
                'overall_sentiment': overallSentiment
            }
        )
        
        for objectName in targetedSentiment:
            
            targetedSentimentTbl.put_item(
                Item={
                    'interaction_id': GUID,
                    'object_name': objectName,
                    'sentiment': targetedSentiment[objectName]
                }
            )
    except ClientError as err:
        logger.error(
            "Couldn't add interaction to table %s. Here's why: %s: %s",
            'interactions',
            err.response['Error']['Code'], err.response['Error']['Message'])
        raise
    
    
    return 'success'
