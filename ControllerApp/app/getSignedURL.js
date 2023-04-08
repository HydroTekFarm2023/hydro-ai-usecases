const {Storage} = require('@google-cloud/storage');

// For more information on ways to initialize Storage, please see
// https://googleapis.dev/nodejs/storage/latest/Storage.html

// Creates a client using Application Default Credentials

// Creates a client from a Google service account key
const storage = new Storage({keyFilename: 'hydrotek-286213-028ddcbed477.json'});


const fileName = 'hydrotek-2022/images/mumbai-hydrotek-farm/station-1/daily-rgb-output-images/t1-output.jpg';

const bucketName = fileName.split("/")[0];
const imageName = fileName.split("/").slice(1,).join("/");
console.log(imageName);

const bucket = storage.bucket(bucketName);
const file = bucket.file(imageName);

var minutesToAdd=10;
var currentDate = new Date();
var futureDate = new Date(currentDate.getTime() + minutesToAdd*60000);
console.log(futureDate.getTime());


file.getSignedUrl({
  action: 'read',
  expires: futureDate.getTime()

}).then(signedUrls => {
   console.log(signedUrls[0]);
});