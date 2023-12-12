import boto3
import os
from io import BytesIO, StringIO
import PyPDF2
import csv
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

def lambda_handler(event, context):
    
    bucket_name = os.environ['bucket_name']
    file_name = event["queryStringParameters"]['file_name']
    
    # Let's extract the business name from the token by looking at the group memebership of the user
    token = event['headers']['Authorization']
    decoded = decode_jwt(token)
    # We only ever expect the user to be in one group only - business rule
    business_name = decoded['cognito:groups'][0]
    folder_loc=f"document/{business_name}"
    reviews_file = f"{folder_loc}/{file_name}"

    try:
        # Fetch the file from S3
        s3 = boto3.client('s3')
        response = s3.get_object(Bucket=bucket_name, Key=reviews_file)
        file_content = response['Body'].read()
        fileType = response['ContentType']
        print("fileType= "+fileType)
        
        # Decide the file type
        if fileType == 'application/pdf':
            # Process PDF
            pdf_reader = PyPDF2.PdfReader(BytesIO(file_content))
            file_data = [pdf_reader.pages[page].extract_text() for page in range(len(pdf_reader.pages))]
        elif fileType == 'text/csv':
            # Process CSV
            csv_file = StringIO(file_content.decode('utf-8'))
            csv_reader = csv.reader(csv_file)
            file_data = [row for row in csv_reader]
        else:
            # Unsupported file type
            raise ValueError("Unsupported file type")
            
        # Call Bedrock for LLM summary
        bedrock = boto3.client('bedrock-runtime')
        body = json.dumps({
                        "prompt": f"\n\nHuman: create a summary of the following and also provide top 5 recommendations based on it. Label the summary with \"Summary\" and recommendations with \"Top 5 recommendations\":\n{file_data} \n\nAssistant:",
            "max_tokens_to_sample": 1800,
            "temperature": 0.5
        })
        modelId = 'anthropic.claude-instant-v1'
        accept = 'application/json'
        contentType = 'application/json'

        response = bedrock.invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)

        response_body = json.loads(response.get('body').read())

        return {
                'statusCode': 200,
                'headers': {
                    "Access-Control-Allow-Headers" : "Content-Type",
                    "Access-Control-Allow-Origin": "https://query.shoutavouch.com",
                    "Access-Control-Allow-Methods": "OPTIONS,PUT,POST,GET"
            },    
                'body': response_body.get('completion')
            }  
    except Exception as e:
        print(e)
        raise e
