from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
import os
import boto3
import json


def lambda_handler(event, context):

    api_key = os.environ['openai_api_key']
    bucket_name = os.environ['bucket_name']
    file_name = event['file_name']
    file_prefix = event['file_prefix']
    s3 = boto3.client('s3')
    
    # Read the S3 file
    try:
        response = s3.get_object(Bucket=bucket_name, Key=file_name)
        content = response['Body'].read().decode('utf-8')
    except Exception as e:
        print(e)
    
    # Prepare the content for embeddings
    text_splitter = CharacterTextSplitter(chunk_size=150, chunk_overlap=0, separator = " ")
    data = []
    data.append(content)
    docs = []
    for i, d in enumerate(data):
        splits = text_splitter.split_text(d)
        docs.extend(splits)
    
    # Here we create a vector store from the documents and save it to disk.
    docsearch = FAISS.from_texts(docs, OpenAIEmbeddings(openai_api_key=api_key))
    docsearch.save_local("/tmp/faiss_index")
    
    index_filename_full = f'{file_prefix}/faiss_index/index.faiss'
    pkl_filename_full = f'{file_prefix}/faiss_index/index.pkl'
    
    # Upload the index to S3
    try:
        s3.upload_file('/tmp/faiss_index/index.faiss', bucket_name, index_filename_full)
        s3.upload_file('/tmp/faiss_index/index.pkl', bucket_name, pkl_filename_full)
        print("Files uploaded to S3")
    except Exception as e:
        print(e)
    
    
    return {
        'statusCode': 200,
        'body': json.dumps('Index created and uploaded!')
    }
