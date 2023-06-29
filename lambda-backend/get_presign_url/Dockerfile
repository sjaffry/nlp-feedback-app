# Dockerfile
FROM public.ecr.aws/lambda/nodejs:14

COPY package*.json ./

RUN npm install

COPY getPresignUrl.js ./

CMD ["getPresignUrl.handler"]
