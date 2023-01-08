import json
import boto3
import random
import os

def lambda_handler(event, context):
    
    s3 = boto3.client('s3')
    bucket = os.environ['bucket_name']
    url_expiration_seconds = 300

    randomID = random.randint(0,10000000)
    Key = f'audio/{randomID}.mp3'

    # Get signed URL from S3
    uploadURL = s3.generate_presigned_url('put_object', Params = {'Bucket': bucket, 'Key': Key}, ExpiresIn = url_expiration_seconds)

    response = {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Headers" : "Content-Type",
            "Access-Control-Allow-Origin": "https://main.d3dsqwcjkun7bv.amplifyapp.com",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
        },
        "body": json.dumps({
            'uploadURL': uploadURL,
            'Key': Key
        }),
        "isBase64Encoded": False
    }

    return response

