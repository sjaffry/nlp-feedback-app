import boto3
import io
import json
from datetime import datetime
import os

class NoDataException(Exception):
    pass

def archive_file(bucket_name, file_key, input_file_prefix):
    s3 = boto3.resource('s3')
    file_name = os.path.basename(file_key)

    copy_source = {
        'Bucket': bucket_name,
        'Key': file_key
    }

    new_key = f'{input_file_prefix}archive/{file_name}'

    # Copy the object to archive folder if it's not already in there and then delete
    if file_key != new_key:
        s3.meta.client.copy(copy_source, bucket_name, new_key)
        s3.Object(bucket_name, file_key).delete()
    
    
def combine_files_in_s3_bucket(bucket_name, output_file_key, input_file_prefix):
    # Create a new S3 client
    s3 = boto3.client('s3')

    # Get a list of all objects in the bucket
    objects = s3.list_objects_v2(Bucket=bucket_name, Prefix=input_file_prefix)
    json_file_exists = any(obj['Key'].endswith('.json') for obj in objects.get('Contents', []))

    if json_file_exists:
        # Create an in-memory file to hold the combined contents
        combined_file = io.StringIO()
    
        # Read the contents of each file and append it to the combined file
        for obj in objects.get('Contents', []):
            file_key = obj['Key']
            if file_key.endswith('.json'):
                obj = s3.get_object(Bucket=bucket_name, Key=file_key)
                contents = obj['Body'].read().decode('utf-8')       
                json_data = json.loads(contents)
                transcript_text = json_data["results"]["transcripts"][0]["transcript"]
                if transcript_text is not None:
                    transcript_text = transcript_text+'. ' #Adding a period in case original review didn't
                    combined_file.write(transcript_text)
                    archive_file(bucket_name, file_key, input_file_prefix)
    
        # Reset the in-memory file pointer to the beginning
        combined_file.seek(0)
        # Store the combined file back into S3
        s3.put_object(Body=combined_file.getvalue(), Bucket=bucket_name, Key=output_file_key)
    
        # Close the in-memory file
        combined_file.close()
    else: 
        raise NoDataException

def lambda_handler(event, context):
    formatted_date = datetime.now().strftime("%Y%m")
    bucket_name = os.environ['bucket_name']
    input_file_prefix = event['input_file_prefix']
    output_file_prefix = f"{event['input_file_prefix']}{formatted_date}"
    output_file_key = f"{output_file_prefix}/combinedreviews.txt"
    # Call the function to combine files in the bucket
    try:
        combine_files_in_s3_bucket(bucket_name, output_file_key, input_file_prefix)
        output = {
            'file_name': output_file_key,
            'file_prefix': output_file_prefix,
            'bucket_name': bucket_name
            }
    except NoDataException:
        # Sending a None in file_name get's handled in the embeddings lambda as nothing to do
        output = {
            'file_name': 'None',
            'file_prefix': 'None'
            }

    return output
