# Dockerfile
FROM public.ecr.aws/lambda/python:3.9

RUN pip install --upgrade pip

COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY getEmbeddings.py ./

CMD ["getEmbeddings.lambda_handler"]
