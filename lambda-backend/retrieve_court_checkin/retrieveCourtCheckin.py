import boto3
from boto3.dynamodb.conditions import Key
import os
import json
    
def lambda_handler(event, context):
    
    # Retrieve 'court_number' and 'checkin_timestamp' from the event
    court_number = event["queryStringParameters"]['court_number']
    checkin_timestamp = event["queryStringParameters"]['checkin_timestamp']
    
    try:
        # Check if both keys are provided
        if not court_number or not checkin_timestamp:
            raise Exception('Error: The court_number and checkin_timestamp must not be null.')
        
        # Create a DynamoDB client
        dynamodb = boto3.resource('dynamodb')
        
        # Specify the table
        tableName = os.environ['table_name']
        table = dynamodb.Table(tableName)
        
        # Fetch the item from the table
        response = table.get_item(
            Key={
                'court_number': int(court_number),
                'checkin_timestamp': int(checkin_timestamp)
            }
        )
        
        # Check if item exists
        item = response.get('Item')
        
        if not item:
            new_item = {
                "court_number": '',
                "checkin_timestamp": '',
                "player_name": ''
            }
        else:
            new_item = {
                "court_number": str(item['court_number']),
                "checkin_timestamp": str(item['checkin_timestamp']),
                "player_name": item['player_name']
            }
        
        return {
            'statusCode': 200,
            'headers': {
                "Access-Control-Allow-Headers" : "Content-Type",
                "Access-Control-Allow-Origin": "https://feedback.onreaction.com",
                "Access-Control-Allow-Methods": "OPTIONS,PUT,POST,GET"
            },    
            'body': json.dumps(new_item)
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