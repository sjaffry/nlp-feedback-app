import os
import boto3
import json
import base64


def decode_base64_url(data):
    """Add padding to the input and decode base64 url"""
    missing_padding = len(data) % 4
    if missing_padding:
        data += '=' * (4 - missing_padding)
    return base64.urlsafe_b64decode(data)

def decode_jwt(token):
    """Split the token and decode each part"""
    parts = token.split('.')
    if len(parts) != 3:  # a valid JWT has 3 parts
        raise ValueError('Token is not valid')

    header = decode_base64_url(parts[0])
    payload = decode_base64_url(parts[1])
    signature = decode_base64_url(parts[2])

    return json.loads(payload)
    #return { 'business_name': payload['cognito:groups'][0] }

def lambda_handler(event, context):
    bucket_name = os.environ['bucket_name']
    appId = os.environ['qbusiness_appId'] 

    query = event["queryStringParameters"]['query']
    prompt_prefix = "Respond in English only. "
    
    # Let's extract the business name from the token by looking at the group memebership of the user
    token = event['headers']['Authorization']
    decoded = decode_jwt(token)
    # We only ever expect the user to be in one group only - business rule
    business_name = decoded['cognito:groups'][0]
    user_name = decoded['cognito:username']
    
    client = boto3.client('qbusiness')
    
    response = client.chat_sync(
        applicationId=appId,
        userId=user_name,
        userMessage=query
    )
    
    result = {
        "answer": response['systemMessage'],
        "sources": [source['title'] for source in response['sourceAttributions']]
    }
    
    return {
        'statusCode': 200,
        'headers': {
            "Access-Control-Allow-Headers" : "Content-Type",
            "Access-Control-Allow-Origin": "https://query.onreaction.com",
            "Access-Control-Allow-Methods": "OPTIONS,PUT,POST,GET"
    },   
        'body': json.dumps(result)
    }
