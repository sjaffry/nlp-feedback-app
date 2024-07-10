import json
import boto3
import os
import hashlib
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')

def caesar_cipher(text, shift):
    obfuscated_text = []
    for char in text:
        if char.isalpha():
            shift_base = 65 if char.isupper() else 97
            obfuscated_text.append(chr((ord(char) - shift_base + shift) % 26 + shift_base))
        else:
            obfuscated_text.append(char)
    return ''.join(obfuscated_text)

def validToken(inputHashToken, court_number, business_name):
    obfuscated_biz_name = caesar_cipher(business_name, 3)
    string_to_hash = f'court{court_number}-{obfuscated_biz_name}'
    input_bytes = string_to_hash.encode('utf-8')
    
    sha256_hash = hashlib.sha256()
    sha256_hash.update(input_bytes)
    # Get the hexadecimal representation of the hash
    hex_digest = sha256_hash.hexdigest()
    
    if (hex_digest == inputHashToken):
        return True
    else:
        return False

def lambda_handler(event, context):
    table_name = os.environ['table_name']
    court_number = event["queryStringParameters"]['court_number']
    business_name = event["queryStringParameters"]['business_name'].lower()
    inputHashToken = event["queryStringParameters"]['input_hash_token']
    first_name_prefix = event["queryStringParameters"]['first_name_prefix'].title()

    table = dynamodb.Table(table_name)
    
    if validToken(inputHashToken, court_number, business_name):
        response = table.scan(
            FilterExpression=Key('first_name').begins_with(first_name_prefix.strip())
        )
    
        # Extract the items from the response
        items = response.get('Items', [])
    else:
        items = []

    
    return {
    'statusCode': 200,
    'headers': {
        "Access-Control-Allow-Headers" : "Content-Type",
        "Access-Control-Allow-Origin": "https://feedback.onreaction.com",
        "Access-Control-Allow-Methods": "OPTIONS,PUT,POST,GET"
    },    
    'body': json.dumps(items)
} 
