from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
import dotenv
import os
import boto3


# Load environment variables from .env file
dotenv.load_dotenv()
# Access environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
bucket_name = os.getenv('bucket_name')
file_name = os.getenv('file_name')
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
docsearch = FAISS.from_texts(docs, OpenAIEmbeddings())
docsearch.save_local("faiss_index")

# Upload the index to S3
try:
    s3.upload_file('./faiss_index/index.faiss', bucket_name, 'faiss_index/index.faiss')
    s3.upload_file('./faiss_index/index.pkl', bucket_name, 'faiss_index/index.pkl')
    print("Files uploaded to S3")
except Exception as e:
    print(e)