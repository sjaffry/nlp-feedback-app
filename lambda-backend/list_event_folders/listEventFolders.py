import json
import boto3
import os

def list_s3_folders(bucket_name, prefix=''):
    s3 = boto3.client('s3')
    
    # Use the list_objects_v2 method to list objects in the bucket
    objects = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix, Delimiter='/')
    
    # Extract the CommonPrefixes, which represent folders
    folders = [folder.get('Prefix') for folder in objects.get('CommonPrefixes', [])]
    
    return folders
    
def lambda_handler(event, context):
    bucket_name = os.environ['bucket_name']
    input_file_prefix = event['input_file_prefix']
    business_name = event['business_name']

    try:
        # List folders within a specific prefix
        subfolder_prefix = f'{input_file_prefix}events/'
        print('subfolder_prefix: '+subfolder_prefix)
        subfolders = list_s3_folders(bucket_name, prefix=subfolder_prefix)
        subfolder_list = []
        
        for folder in subfolders:
              subfolder_list.append({ "input_file_prefix": folder, "business_name": business_name }) 
            
        output = {
                  "detail": {
                    "subfolders": subfolder_list
                  }
                }
    except:
        # Sending a None in file_name get's handled in the embeddings lambda as nothing to do
        output = {
                  "detail": {
                    "subfolders": []
                  }
                }

    return output