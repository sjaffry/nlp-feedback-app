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
    
    
def combine_files_in_s3_bucket(bucket_name, output_file_key, input_file_prefix, review_count_file_key):
    # Create a new S3 client
    s3 = boto3.client('s3')

    # Get a list of all objects in the bucket including those in the archive folder by ommitting the "Delimeter" option)
    objects = s3.list_objects_v2(Bucket=bucket_name, Prefix=input_file_prefix)
    json_file_exists = any(obj['Key'].endswith('.json') for obj in objects.get('Contents', []))

    if json_file_exists:
        # Create an in-memory file to hold the combined contents
        combined_file = io.StringIO()
        count_file = io.StringIO()
        review_count = 0
    
        # Read the contents of each file and append it to the combined file
        for obj in objects.get('Contents', []):
            file_key = obj['Key']
            if file_key.endswith('.json'):
                review_count += 1
                obj = s3.get_object(Bucket=bucket_name, Key=file_key)
                contents = obj['Body'].read().decode('utf-8')       
                json_data = json.loads(contents)
                transcript_text = json_data["results"]["transcripts"][0]["transcript"]
                if transcript_text is not None:
                    transcript_text = transcript_text.replace(',', '')
                    transcript_text += '\n'
                    combined_file.write(transcript_text)
                    archive_file(bucket_name, file_key, input_file_prefix)

        count_file.write(str(review_count))

        # Reset the in-memory file pointer to the beginning
        combined_file.seek(0)
        # Store the combined file back into S3
        s3.put_object(Body=combined_file.getvalue(), Bucket=bucket_name, Key=output_file_key)
        # Record the number of reviews combined
        s3.put_object(Body=count_file.getvalue(), Bucket=bucket_name, Key=review_count_file_key)
    
        # Close the in-memory file
        combined_file.close()
    else: 
        raise NoDataException

def get_active_event(business_name):
    dynamodb = boto3.resource('dynamodb')

    # Reference to the 'events' table
    table = dynamodb.Table('events')
    
    try:
        
        response = table.query(
            KeyConditionExpression='business_name = :bn',
            FilterExpression='active = :act',
            ExpressionAttributeValues={
                ':bn': business_name,
                ':act': 'Y',
            }
        )
        
        # There should only ever be 1 active event in the table
        items = response['Items']
        if len(items) > 1:
            raise TooManyItemsException
        elif len(items) == 0:        
            event_name = 'None'
        else:
            event_name = items[0].get('event_name')
        
    except NoDataException:
        raise NoDataException
    
    return event_name


def moveObjectsFromVanilla(bucket_name, event_name, business_name):
    # Create an S3 client
    s3 = boto3.client('s3')
    source_folder = f'transcribe-output/{business_name}/events/vanilla/'
    target_folder = f'transcribe-output/{business_name}/events/{event_name}/'
    
    # List objects within the source folder
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=source_folder)
    
    if 'Contents' in response:
        for item in response['Contents']:
            # Define the source object
            copy_source = {
                'Bucket': bucket_name,
                'Key': item['Key']
            }
            
            # Define the new key (path) for the object in the target folder
            new_key = item['Key'].replace(source_folder, target_folder, 1)
            
            # Copy the object to the new location
            s3.copy_object(Bucket=bucket_name, CopySource=copy_source, Key=new_key)
            
            # Delete the original object
            s3.delete_object(Bucket=bucket_name, Key=item['Key'])

def lambda_handler(event, context):
    formatted_date = datetime.now().strftime("%Y%m")
    bucket_name = os.environ['bucket_name']
    business_name = event['business_name']
    input_file_prefix = event['input_file_prefix']

    # Get the active event name if not provided as input
    if (input_file_prefix == 'transcribe-output/FTSC/events/vanilla/'):
        event_name = get_active_event(business_name)
        moveObjectsFromVanilla(bucket_name, event_name, business_name)
        source_file_prefix = f'transcribe-output/{business_name}/events/{event_name}/'
    else:
        source_file_prefix = input_file_prefix

    target_file_prefix = f'{source_file_prefix}{formatted_date}'
    output_file_key = f"{target_file_prefix}/combinedreviews.txt"
    review_count_file_key = f"{target_file_prefix}/reviewcount.txt"

    # Call the function to combine files in the bucket
    try:
        combine_files_in_s3_bucket(bucket_name, output_file_key, source_file_prefix, review_count_file_key)

        output = {
            'file_name': output_file_key,
            'file_prefix': target_file_prefix,
            'bucket_name': bucket_name
            }
    except NoDataException:
        # Sending a None in file_name get's handled in the embeddings lambda as nothing to do
        output = {
            'file_name': 'None',
            'file_prefix': 'None'
            }

    return output

