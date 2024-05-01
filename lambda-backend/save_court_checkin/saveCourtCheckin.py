import boto3
from boto3.dynamodb.conditions import Key
import os
import json
import random

def get_random_key():

    min_value = 100000000000
    max_value = 999999999999
    
    return random.randint(min_value, max_value)

def lambda_handler(event, context):
    
    # Retrieve 'court_number' and 'checkin_timestamp' from the event
    court_number = event["queryStringParameters"]['court_number']
    checkin_timestamp = event["queryStringParameters"]['checkin_timestamp']   
    player_name = event["queryStringParameters"]['player_name'] 
    business_name = event["queryStringParameters"]['business_name']
    keep_warm = event["queryStringParameters"]['keep_warm']
    dynamodb = boto3.resource('dynamodb')
    
    if keep_warm == "true":
        return {'body': json.dumps('stay warm!')}
    
    try:
        # Check if both keys are provided
        if not court_number or not checkin_timestamp or not business_name:
            raise Exception('Error: The business_name, court_number or checkin_timestamp must not be null.')
        
        # Specify the table
        tableName = os.environ['table_name']
        table = dynamodb.Table(tableName)
        
        response = table.put_item(
            Item={
                'business_name': business_name,
                'random_key': get_random_key(),
                'court_number': court_number,
                'player_name': player_name,
                'checkin_timestamp': checkin_timestamp
            }
        )
        
        return {
            'statusCode': response['ResponseMetadata']['HTTPStatusCode'],
            'headers': {
                "Access-Control-Allow-Headers" : "Content-Type",
                "Access-Control-Allow-Origin": "https://feedback.onreaction.com",
                "Access-Control-Allow-Methods": "OPTIONS,PUT,POST,GET"
            },    
            'body': json.dumps('Check-in Saved!')
        } 
    
    except Exception as e:
        print(e)
        return {
            'statusCode': 500,
            'headers': {
                "Access-Control-Allow-Headers" : "Content-Type",
                "Access-Control-Allow-Origin": "https://feedback.onreaction.com",
                "Access-Control-Allow-Methods": "OPTIONS,PUT,POST,GET"
            },
            'body': json.dumps('An error occurred: ' + str(e))
        }