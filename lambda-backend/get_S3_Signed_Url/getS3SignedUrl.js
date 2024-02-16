const AWS = require('aws-sdk');
const crypto = require('crypto');


// Setup AWS configurations
AWS.config.update({region: 'us-west-2'}); 
// S3 client
const s3 = new AWS.S3({
  apiVersion: '2006-03-01',
  signatureVersion: 'v4',
});
const URL_EXPIRATION_SECONDS = 300
// Create DynamoDB document client
const docClient = new AWS.DynamoDB.DocumentClient();


const hashSha256 = (inputString) => {
  const hash = crypto.createHash('sha256');
  hash.update(inputString);
  // Convert the hash to a hexadecimal string
  return hash.digest('hex');
}

const getBusinessFromDB = async (input_business_hash) => {

    const table_name = process.env.table_name;
    const uniqueKeys = new Set();
    let params = {
        TableName: table_name,
        ProjectionExpression: 'business_name',
    };
    
    let items;
    do {
        items = await docClient.scan(params).promise();
        items.Items.forEach(item => {
            uniqueKeys.add(item['business_name']);
        });

        // Prepare the next scan operation if there's more data
        params.ExclusiveStartKey = items.LastEvaluatedKey;
    } while (items.LastEvaluatedKey);

    return Array.from(uniqueKeys);
}

const getEventsFromDB = async (business_name, input_event_hash) => {

    const table_name = process.env.table_name;
    // Define the parameters for the query
    const params = {
        TableName: table_name,
        KeyConditionExpression: '#bn = :businessName',
        ExpressionAttributeNames: {
            '#bn': 'business_name',
        },
        ExpressionAttributeValues: {
            ':businessName': business_name
        },
    };
    
    let eventName;

    try {
        // Check if event name matches the events in the database
        const data = await docClient.query(params).promise();
         for (let item of data.Items) {
            if (input_event_hash === hashSha256(item['event_name'])) {
              eventName = item['event_name'];
              break;
            }
        }
        // Return the query results
        return eventName;
    }
    catch (err) {
        console.error("Unable to query. Error:", JSON.stringify(err, null, 2));
        return err
    }
}

const extractQSParams = async (qs) => {

  const splitStrings = qs.split("/");

  let businessName;
  let eventName;
  let inputBusinessHash;
  let inputEventHash;


  if (splitStrings[0]) {
    inputBusinessHash = splitStrings[0].toLowerCase();
  }

  if (splitStrings[1]) {
    inputEventHash = splitStrings[1].toLowerCase();
  }


  const businessNameList = await getBusinessFromDB(inputBusinessHash);
  
  //Check business name
  for (let bn of businessNameList) {
      if (hashSha256(bn) === inputBusinessHash) {
          businessName = bn;
          break;
      }
  }

  if (!businessName) {
      throw new Error("business_name not found");
  }

  // If the event is Vanilla no need to check in database
  if (hashSha256('vanilla') != inputEventHash) {
    eventName = await getEventsFromDB(businessName, inputEventHash);  
  } else { eventName = 'vanilla' };
  
  
  return {
    business_name: businessName,
    event_name: eventName
  };

}

const getUploadURL = async (business_name, event_name, upload_dir, file_name) => {
  const randomID = parseInt(Math.random() * 10000000)
  const Key = (!event_name) ? `${upload_dir}/${business_name}/${file_name}` : `${upload_dir}/${business_name}/events/${event_name}/${file_name}`


  // Get signed URL from S3
  const s3Params = {
    Bucket: process.env.bucket_name,
    Key,
    Expires: URL_EXPIRATION_SECONDS,
    ContentType: 'application/octet-stream'
  }
  const uploadURL = await s3.getSignedUrlPromise('putObject', s3Params);

  const response = {
      "statusCode": 200,
      "headers": {
            "Access-Control-Allow-Headers" : "Content-Type",
            "Access-Control-Allow-Origin": "https://feedback.onreaction.com",
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

exports.handler = async (event) => {
  const inputHash = event["queryStringParameters"]["qs"]
  const qs_params = await extractQSParams(inputHash);
  const business_name = qs_params["business_name"]
  const event_name = qs_params["event_name"]
  const upload_dir = event["queryStringParameters"]["upload_dir"]
  const file_name = event["queryStringParameters"]["file_name"]
  return await getUploadURL(business_name, event_name, upload_dir, file_name);
};

