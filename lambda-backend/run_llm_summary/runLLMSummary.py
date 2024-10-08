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

def lambda_handler(event, context):

    bucket_name = os.environ['bucket_name']
    date_range = event["queryStringParameters"]['date_range']
    event_name = event["queryStringParameters"]['event_name']
    
    # Let's extract the business name from the token by looking at the group memebership of the user
    token = event['headers']['Authorization']
    decoded = decode_jwt(token)
    # We only ever expect the user to be in one group only - business rule
    business_name = decoded['cognito:groups'][0]
    folder_loc = (
    "transcribe-output/"
    + f"{business_name}/"
     + (f"events/{event_name}/" if event_name else "")
    + f"{date_range}"
    )
    
    reviews_file = f"{folder_loc}/combinedreviews.txt"
    reviews_count_file = f"{folder_loc}/reviewcount.txt"


    # Fetch the file from S3
    s3 = boto3.client('s3')
    
    # Let's read the reviews file
    response = s3.get_object(Bucket=bucket_name, Key=reviews_file)
    file_data = response['Body'].read()
    
    # Let's read the review count file
    count_response = s3.get_object(Bucket=bucket_name, Key=reviews_count_file)
    count = count_response['Body'].read().decode('utf-8')
    
    # Call Bedrock for LLM summary
    bedrock = boto3.client('bedrock-runtime')
    prompt = f"create a 3 paragraph summary of the following feedback from club members and also provide top 5 recommendations based on it. Label the summary with \"Summary\" and recommendations with \"Top 5 recommendations\":\n{file_data}"
    model_id = 'anthropic.claude-3-haiku-20240307-v1:0'
    
    try:
        response = bedrock.invoke_model(
            modelId=model_id,
            body=json.dumps(
                {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 1800,
                    "messages": [
                        {
                            "role": "user",
                            "content": [{"type": "text", "text": prompt}],
                        }
                    ],
                }
            ),
        )

        # Process and print the response
        result = json.loads(response.get("body").read())
        input_tokens = result["usage"]["input_tokens"]
        output_tokens = result["usage"]["output_tokens"]
        output_list = result.get("content", [])

        print("Invocation details:")
        print(f"- The input length is {input_tokens} tokens.")
        print(f"- The output length is {output_tokens} tokens.")

        print(f"- The model returned {len(output_list)} response(s):")
        llmtext = ''
        for output in output_list:
            llmtext += output["text"]

        final_output = {
            "llm_text": llmtext,
            "review_count": count
        }
        
        return {
            'statusCode': 200,
            'headers': {
                "Access-Control-Allow-Headers" : "Content-Type",
                "Access-Control-Allow-Origin": "https://query.onreaction.com",
                "Access-Control-Allow-Methods": "OPTIONS,PUT,POST,GET"
            },    
            'body': json.dumps(final_output)
        } 

    except Exception as e:
        print(e)
        raise e