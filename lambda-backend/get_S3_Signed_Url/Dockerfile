# Dockerfile
FROM public.ecr.aws/lambda/nodejs:14

COPY package*.json ./

RUN npm install

COPY getS3SignedUrl.js ./

CMD ["getS3SignedUrl.handler"]
