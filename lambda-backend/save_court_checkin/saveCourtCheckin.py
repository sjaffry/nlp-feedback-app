import boto3
from boto3.dynamodb.conditions import Key
import os
import json

def lambda_handler(event, context):
    
    # Retrieve 'court_number' and 'checkin_timestamp' from the event
    court_number = event["queryStringParameters"]['court_number']
    checkin_timestamp = event["queryStringParameters"]['checkin_timestamp']   
    player_name = event["queryStringParameters"]['player_name'] 
    
    try:
        # Check if both keys are provided
        if not court_number or not checkin_timestamp:
            raise Exception('Error: The court_number and checkin_timestamp must not be null.')
            
        # Create a DynamoDB client
        dynamodb = boto3.resource('dynamodb')
        
        # Specify the table
        tableName = os.environ['table_name']
        table = dynamodb.Table(tableName)
        
        response = table.update_item(
            Key={
                'court_number': int(court_number),
                'checkin_timestamp': int(checkin_timestamp)
            },
            UpdateExpression="set player_name=:p",
            ExpressionAttributeValues={
                ':p': player_name,
            },
            ReturnValues="UPDATED_NEW"
        )
        
        return {
            'statusCode': response['ResponseMetadata']['HTTPStatusCode'],
            'headers': {
                "Access-Control-Allow-Headers" : "Content-Type",
                "Access-Control-Allow-Origin": "https://checkin.onreaction.com",
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
                "Access-Control-Allow-Origin": "https://checkin.onreaction.com",
                "Access-Control-Allow-Methods": "OPTIONS,PUT,POST,GET"
            },
            'body': json.dumps('An error occurred: ' + str(e))
        }