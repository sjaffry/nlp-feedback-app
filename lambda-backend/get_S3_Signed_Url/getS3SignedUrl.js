const AWS = require('aws-sdk')
const crypto = require('crypto');
const s3 = new AWS.S3({
  apiVersion: '2006-03-01',
  signatureVersion: 'v4',
});
const URL_EXPIRATION_SECONDS = 300

function hashSha256(inputString) {
  const hash = crypto.createHash('sha256');
  hash.update(inputString);
  // Convert the hash to a hexadecimal string
  return hash.digest('hex');
}

function extractQueryStringParams(qs) {

  // TODO - Retrieve this list from DynamoDB later
  const businessNameList = ["FTSC"];
  const eventNameList = ["warmpoolday","halloween","diwali"];
  const splitStrings = qs.split("/");

  let businessName;
  let eventName;

  // Check business name
  for (let bn of businessNameList) {
      if (hashSha256(bn) === splitStrings[0]) {
          businessName = bn;
          break;
      }
  }

  if (!businessName) {
      throw new Error("business_name not found");
  }

  // Check event name
  for (let en of eventNameList) {
      if (hashSha256(en) === splitStrings[1]) {
          eventName = en;
          break;
      }
  }

  if (!eventName) {
      throw new Error("event name not found");
  }

  const result = {
      business_name: businessName,
      event_name: eventName
  };

  return result;
}

// Main Lambda entry point
exports.handler = async (event) => {
  const inputHash = event["queryStringParameters"]["qs"]
  const qs_params = extractQueryStringParams(inputHash);
  const business_name = qs_params["business_name"]
  const upload_dir = event["queryStringParameters"]["upload_dir"]
  const file_name = event["queryStringParameters"]["file_name"]
  const event_name = qs_params["event_name"]
  return await getUploadURL(business_name, event_name, upload_dir, file_name);
}

const getUploadURL = async function(business_name, event_name, upload_dir, file_name) {
  const randomID = parseInt(Math.random() * 10000000)
  const Key = (!event_name) ? `${upload_dir}/${business_name}/${file_name}` : `${upload_dir}/${business_name}/events/${event_name}/${file_name}`


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