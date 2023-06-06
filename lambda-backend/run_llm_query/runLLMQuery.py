from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA
from langchain.vectorstores import FAISS
import os
import boto3
import json

def download_index_files(bucket_name, index_file, pkl_file, local_index_file, local_pkl_file):
    s3 = boto3.client('s3')
    try:
        s3.download_file(bucket_name, index_file, local_index_file)
        s3.download_file(bucket_name, pkl_file, local_pkl_file)
        print("Files downloaded successfully.")
    except Exception as e:
        raise ValueError(e)

def lambda_handler(event, context):

    api_key = os.environ['openai_api_key']
    bucket_name = os.environ['bucket_name']
    date_range = event["queryStringParameters"]['date_range']
    business_name = event["queryStringParameters"]['business_name']
    query = event["queryStringParameters"]['query']
    index_loc=f"transcribe-output/{business_name}/{date_range}/faiss_index"
    index_file = f"{index_loc}/index.faiss"
    pkl_file = f"{index_loc}/index.pkl"

    # Download faiss index files if not already exist
    local_path = f"/tmp/faiss_index_{business_name}"
    local_index_file = f"{local_path}/index.faiss"
    local_pkl_file = f"{local_path}/index.pkl"

    if not(os.path.isfile(local_index_file) and os.path.isfile(local_pkl_file)):
            os.mkdir(local_path)
            download_index_files(bucket_name, index_file, pkl_file, local_index_file, local_pkl_file)
    else:
        print("Files already exists no need to download")

    # Load faiss index
    docsearch = FAISS.load_local(local_path, OpenAIEmbeddings(openai_api_key=api_key))

    # Initialize the retrieval chain and run LLM query
    try:
        qa = RetrievalQA.from_chain_type(OpenAI(openai_api_key=api_key), chain_type="stuff", retriever=docsearch.as_retriever())
        result = qa.run(query)
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