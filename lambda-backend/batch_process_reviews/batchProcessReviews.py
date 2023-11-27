import boto3
import pandas as pd
from datetime import datetime, timedelta
from io import StringIO
import io
import os
import json

def store_all_reviews(df, output_loc, bucket_name, s3_client):
    reviews_file = io.StringIO()
    output_file_key = f'{output_loc}/allreviews.txt'
    df['review_text'].to_csv(reviews_file, index=False, header=False)
    # Reset the in-memory file pointer to the beginning
    reviews_file.seek(0)
    # Store the combined file back into S3
    s3_client.put_object(Body=reviews_file.getvalue(), Bucket=bucket_name, Key=output_file_key)

    
def store_reviews_by_period(df, output_loc, bucket_name, s3_client):
    # Group the DataFrame by 2 weeks
    groups = df.groupby(pd.Grouper(key='date', freq='M'))

    # Write each group to a separate CSV file in S3
    for name, group in groups:
        # Format the name to 'MMYYYY'
        file_name = name.strftime('%Y%m')
        reviews_file = io.StringIO()
        s3_file_name = f'{output_loc}/{file_name}30/combinedreviews.txt'
        group['review_text'].to_csv(reviews_file, index=False, header=False)
        s3_client.put_object(Body=reviews_file.getvalue(), Bucket=bucket_name, Key=s3_file_name)
        

def lambda_handler(event, context):
    s3 = boto3.client('s3')
    bucket_name = os.environ['bucket_name']
    business_name = event['business_name']
    time_interval = event['time_interval']
    input_file_name = f'batch/input/{business_name}/glue_processed/{business_name}-processed.csv'
    output_loc_llm = f'transcribe-output/{business_name}'
    output_loc_sentiment = f'batch/input/{business_name}'
    
    # Get the object from the event and show its content type
    csv_obj = s3.get_object(Bucket=bucket_name, Key=input_file_name)
    body = csv_obj['Body']
    csv_data = body.read().decode('utf-8')
    
    df = pd.read_csv(StringIO(csv_data))
    
    # Convert the 'Date' column to datetime format
    df['date'] = pd.to_datetime(df['date'])
    
    # Get the date n days ago from today as per input time interval
    n_days_ago = datetime.now() - timedelta(days=time_interval)
    
    # Create a mask for all dates within the last n days
    mask = (df['date'] > n_days_ago)
    
    # Use the mask to filter the DataFrame
    df = df.loc[mask]
    
    store_reviews_by_period(df, output_loc_llm, bucket_name, s3)
    store_all_reviews(df, output_loc_sentiment, bucket_name, s3)

    return {
        'statusCode': 200,
        'body': json.dumps('Success')
    }
