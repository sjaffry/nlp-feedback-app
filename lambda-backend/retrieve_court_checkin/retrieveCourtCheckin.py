import boto3
from boto3.dynamodb.conditions import Key, Attr
import os
import json
    
def lambda_handler(event, context):
    
    # Retrieve 'court_number' and 'checkin_timestamp' from the event
    court_number = event["queryStringParameters"]['court_number']
    checkin_timestamp = event["queryStringParameters"]['checkin_timestamp'] 
    business_name = event["queryStringParameters"]['business_name'] 
    
    try:
        # Check if both keys are provided
        if not court_number or not checkin_timestamp:
            raise Exception('Error: The court_number and checkin_timestamp must not be null.')
        
        # Create a DynamoDB client
        dynamodb = boto3.resource('dynamodb')
        
        # Specify the table
        tableName = os.environ['table_name']
        table = dynamodb.Table(tableName)
        
        
        # Fetch items from the table with a condition on checkin_timestamp
        response = table.query(
            KeyConditionExpression=Key('business_name').eq(business_name),
            FilterExpression=Attr('checkin_timestamp').eq(checkin_timestamp) & Attr('court_number').eq(court_number)
        )
        
        # Check if item exists. There will only ever be one item returned for this
        item = response.get('Items')
        
        if not item:
            new_item = {
                "court_number": '',
                "checkin_timestamp": '',
                "player_name": ''
            }
        else:
            new_item = {
                "court_number": item[0]['court_number'],
                "checkin_timestamp": item[0]['checkin_timestamp'],
                "player_name": item[0]['player_name']
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