const AWS = require('aws-sdk')
const s3 = new AWS.S3({
  apiVersion: '2006-03-01',
  signatureVersion: 'v4',
});
const URL_EXPIRATION_SECONDS = 300

// Main Lambda entry point
exports.handler = async (event) => {
  const business_name = event["queryStringParameters"]["business_name"]
  const upload_dir = event["queryStringParameters"]["upload_dir"]
  const file_name = event["queryStringParameters"]["file_name"]
  return await getUploadURL(business_name, upload_dir, file_name)
}

const getUploadURL = async function(business_name, upload_dir, file_name) {
  const randomID = parseInt(Math.random() * 10000000)
  const Key = `${upload_dir}/${business_name}/${file_name}`

  // Get signed URL from S3
  const s3Params = {
    Bucket: process.env.UploadBucket,
    Key,
    Expires: URL_EXPIRATION_SECONDS,
    ContentType: 'application/octet-stream'
  }
  const uploadURL = await s3.getSignedUrlPromise('putObject', s3Params)

  const response = {
      "statusCode": 200,
      "headers": {
            "Access-Control-Allow-Headers" : "Content-Type",
            "Access-Control-Allow-Origin": "https://www.shoutavouch.com",
            "Access-Control-Allow-Methods": "OPTIONS,PUT,POST,GET"
        },
      "body": JSON.stringify({
        uploadURL,
        Key
      }),
      "isBase64Encoded": false
  };

  return response;
}