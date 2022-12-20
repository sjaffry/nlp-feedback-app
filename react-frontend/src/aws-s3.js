import s3 from 'aws-sdk/clients/s3';

function fileUploader(blob, key) {
    const s3 = new s3();

    s3.upload({
        Bucket: 'nlp-feedback-app',
        Key: key,
        Body: blob
    });
}