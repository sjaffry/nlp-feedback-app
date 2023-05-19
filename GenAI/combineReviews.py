import boto3
import io
import json
from datetime import datetime
    
def combine_files_in_s3_bucket(bucket_name, output_file_key, input_file_prefix):
    # Create a new S3 client
    s3 = boto3.client('s3')

    # Get a list of all objects in the bucket
    response = s3.list_objects(Bucket=bucket_name, Prefix=input_file_prefix)
    files = response['Contents']

    # Create an in-memory file to hold the combined contents
    combined_file = io.StringIO()

    # Read the contents of each file and append it to the combined file
    for file in files:
        file_key = file['Key']
        if file_key.split(".")[1] == "json":
            obj = s3.get_object(Bucket=bucket_name, Key=file_key)
            contents = obj['Body'].read().decode('utf-8')       
            json_data = json.loads(contents)
            transcript_text = json_data["results"]["transcripts"][0]["transcript"]
            if transcript_text is not None:
                combined_file.write(transcript_text)

    # Reset the in-memory file pointer to the beginning
    combined_file.seek(0)
    # Store the combined file back into S3
    s3.put_object(Body=combined_file.getvalue(), Bucket=bucket_name, Key=output_file_key)

    # Close the in-memory file
    combined_file.close()

# Inputs to the combine file function
formatted_date = datetime.now().strftime("%Y%m%d")
bucket_name = 'nlp-feedback-app'
output_file_key = f'transcribe-output/Tesla/{formatted_date}/combined_file.txt'
input_file_prefix = 'transcribe-output/Tesla'

# Call the function to combine files in the bucket
combine_files_in_s3_bucket(bucket_name, output_file_key, input_file_prefix)