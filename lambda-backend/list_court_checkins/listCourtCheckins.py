import os
import boto3
from boto3.dynamodb.conditions import Key
import json
import base64

# Create a DynamoDB client
dynamodb = boto3.resource('dynamodb')
# Select your DynamoDB table
tableName = os.environ['table_name']
table = dynamodb.Table(tableName)

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

def lambda_handler(event, context):
    # Let's extract the business name from the token by looking at the group membership of the user
    token = event['headers']['Authorization']
    decoded = decode_jwt(token)
    keep_warm = event["queryStringParameters"]['keep_warm']
    # We only ever expect the user to be in one group only - business rule
    business_name = decoded['cognito:groups'][0]
    user_name = decoded['cognito:username']
    
    if keep_warm == "true":
        return {'body': json.dumps('stay warm!')}
    
    # Fetch all items from the table filtered by business_name
    try:
        response = table.scan(
            FilterExpression=Key('business_name').eq(business_name)
        )
        items = response['Items']
        
        # Continue scanning if there are more items
        while 'LastEvaluatedKey' in response:
            response = table.scan(
                FilterExpression=Key('business_name').eq(business_name),
                ExclusiveStartKey=response['LastEvaluatedKey']
            )
            items.extend(response['Items'])
            
        items_no_businessname = [{k: v for k, v in item.items() if k != 'business_name'} for item in items]
        items_no_randomkey = [{k: v for k, v in item.items() if k != 'random_key'} for item in items_no_businessname]

        # Dictionaries to hold the separated data
        pickleball_dict = []
        tennis_dict = []
        
        # Iterate over each item in the data
        for i, item in enumerate(items_no_randomkey):
            if item["court_number"].startswith("Pickleball"):
                pickleball_dict.append(item)
            else:
                tennis_dict.append(item)

        output = {
            "tennis": tennis_dict,
            "pickleball": pickleball_dict
        }
        
        return {
            'statusCode': 200,
            'headers': {
                "Access-Control-Allow-Headers" : "Content-Type",
                "Access-Control-Allow-Origin": "https://query.onreaction.com",
                "Access-Control-Allow-Methods": "OPTIONS,PUT,POST,GET"
            }, 
            'body': json.dumps(output)
        }
    except Exception as e:
        print(e)
        return {
            'statusCode': 500,
            'headers': {
                "Access-Control-Allow-Headers" : "Content-Type",
                "Access-Control-Allow-Origin": "https://query.onreaction.com",
                "Access-Control-Allow-Methods": "OPTIONS,PUT,POST,GET"
            }, 
            'body': json.dumps("Error retrieving items from DynamoDB")
        }
