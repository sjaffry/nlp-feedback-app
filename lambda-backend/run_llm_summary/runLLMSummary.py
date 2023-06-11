from langchain import OpenAI, PromptTemplate, LLMChain
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains.mapreduce import MapReduceChain
from langchain.docstore.document import Document
from langchain.chains.summarize import load_summarize_chain
from langchain.document_loaders import TextLoader
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

def download_reviews_file(bucket_name, reviews_file, local_reviews_file):
    s3 = boto3.client('s3')
    try:
        s3.download_file(bucket_name, reviews_file, local_reviews_file)
        print("Files downloaded successfully.")
    except Exception as e:
        raise ValueError(e)

def lambda_handler(event, context):

    api_key = os.environ['openai_api_key']
    bucket_name = os.environ['bucket_name']
    date_range = event["queryStringParameters"]['date_range']
    
    # Let's extract the business name from the token by looking at the group memebership of the user
    token = event['headers']['Authorization']
    decoded = decode_jwt(token)
    # We only ever expect the user to be in one group only - business rule
    business_name = decoded['cognito:groups'][0]

    # Download review content file if not already exist
    folder_loc=f"transcribe-output/{business_name}/{date_range}"
    reviews_file = f"{folder_loc}/combinedreviews.txt"
    local_path = f"/tmp/reviews_file_{business_name}"
    local_reviews_file = f"{local_path}/combinedreviews.txt"

    if not(os.path.isfile(local_reviews_file)):
            os.mkdir(local_path)
            download_reviews_file(bucket_name, reviews_file, local_reviews_file)
    else:
        print("Files already exists no need to download")

    # Break up the combined reviews into chunks
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0, separator = " ")
    loader = TextLoader(local_reviews_file)
    documents = loader.load()
    docs = text_splitter.split_documents(documents)
    
    # Initialize the summary chain and run LLM summarization
    try:
        llm = OpenAI(openai_api_key=api_key, temperature=0)
        chain = load_summarize_chain(llm, chain_type="map_reduce")
        result = chain.run(docs)
    except Exception as e:
        raise ValueError(e)

    return {
            'statusCode': 200,
            'headers': {
                "Access-Control-Allow-Headers" : "Content-Type",
                "Access-Control-Allow-Origin": "https://query.shoutavouch.com",
                "Access-Control-Allow-Methods": "OPTIONS,PUT,POST,GET"
        },    
            'body': json.dumps(result)
        }    