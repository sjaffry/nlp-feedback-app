const AWS = require('aws-sdk')
AWS.config.update({ region: 'us-east-1' })
const s3 = new AWS.S3({
  apiVersion: '2006-03-01',
  signatureVersion: 'v4',
});
const URL_EXPIRATION_SECONDS = 300

// Main Lambda entry point
exports.handler = async (event) => {
  return await getUploadURL(event)
}

const getUploadURL = async function(event) {
  const randomID = parseInt(Math.random() * 10000000)
  const Key = `audio/${randomID}.mp3`

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
      "headers": {},
      "body": JSON.stringify({
        uploadURL,
        Key
      }),
      "isBase64Encoded": false
  };

  return response;
}
