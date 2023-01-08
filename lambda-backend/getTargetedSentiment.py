import json
import boto3

def lambda_handler(event, context):
    

    comprehend = boto3.client(service_name='comprehend', region_name='us-east-1')
    s3 = boto3.client('s3')
    bucket = event['bucket_name']
    transcribe_output_prefix = 'transcribe-output'
    job_name = event['transcript_job_name']
    business_name = event['business_name']
    
    print('Calling DetectTargetedSentiment')
    # Opening JSON file
    key = '{}/{}/{}.json'.format(transcribe_output_prefix,business_name,job_name)
    data = s3.get_object(Bucket=bucket, Key=key)
    content = data['Body'].read().decode("utf-8")
    json_content = json.loads(content)
    text = json_content['results']['transcripts'][0]['transcript']

    # Detect targeted sentiment
    targeted_sentiment = comprehend.detect_targeted_sentiment(Text=text, LanguageCode='en')
    objects = []
    object_sentiments = []
    for i in range(len(targeted_sentiment['Entities'])):
        objects.append(targeted_sentiment["Entities"][i]["Mentions"][0]["Text"])
        object_sentiments.append(targeted_sentiment["Entities"][i]["Mentions"][0]["MentionSentiment"]["Sentiment"])
    
    output = {objects[i]: object_sentiments[i] for i in range(len(objects))}
    
    return output

