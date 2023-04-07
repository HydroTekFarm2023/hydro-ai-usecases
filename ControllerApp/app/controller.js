const express = require('express');
const MongoClient = require('mongodb').MongoClient;
const request = require('request');
const http = require("http");
const loadDB = require('./database');
const detect = require('./detection');
const classify = require('./classification');
const growth = require('./growth');
const sendNotification = require('./sendNotification');
const {Storage} = require('@google-cloud/storage');
const thermal = require('./thermal');
const addNotification = require('./addNotification');
const storage = new Storage({keyFilename: './hydrotek-286213-028ddcbed477.json'});
var cors = require('cors');

// use it before all route definitions




const app = express();
app.use(express.json())
const PORT = 3000;

app.use(cors({origin: '*'}));


var ImagePath;
var PlantType;
var apitype;
var CustomerDb;
var HostIP;


async function getDetectNotification(body, data)
{
    console.log(body);
    console.log(Object.keys(body));
    var today = new Date();
    var date = today.getFullYear()+'-'+(today.getMonth()+1)+'-'+today.getDate();
    var time = today.getHours() + ":" + today.getMinutes() + ":" + today.getSeconds();
    var dateTime = date+' '+time;
    var pests = [];
    var messages = [];
    for(var i=0;i<body["pest"].length;i++)
    {
      if(pests.includes(body["pest"][i]))
      {
        continue;
      }
      else
      {
        pests.push(body["pest"][i]);
        

        const fileName = body["image"];
        const bucketName = fileName.split("/")[0];
        const imageName = fileName.split("/").slice(1,).join("/");


        const bucket = storage.bucket(bucketName);
        const file = bucket.file(imageName);
        const signedUrls = await file.getSignedUrl({
          action: 'read',
          expires: '03-09-2491'

        });
        
          console.log(signedUrls[0]);
          var url = signedUrls[0];
          var record = {
            title: 'Pest Detected at '+data.station,
            body: body["pest"][i] + ' was detected on '+data.plant+' station-1. '+body["treatment"][i],
            station: data.station,
            plant: data.plant,
            image: body["image"],
            timestamp: dateTime
          };

          addNotification(record, 'pest-detect-notifications');
          var message = {
            notification: {
              title: 'Pest Detected at '+data.station,
              body: body["pest"][i] + ' was detected on '+data.plant+' station-1. '+body["treatment"][i]
            },
            android: {
              notification: {
                imageUrl: url
              }
            },
            apns: {
              payload: {
                aps: {
                  'mutable-content': 1
                }
              },
              fcm_options: {
                image: url
              }
            },
            webpush: {
              headers: {
                image: url
              }
            }
          };




          messages.push(message);
          
        

      }
    }
    
    return messages;
}


async function getClassifyNotification(body, data)
{
    console.log(body);
    console.log(Object.keys(body));
    var today = new Date();
    var date = today.getFullYear()+'-'+(today.getMonth()+1)+'-'+today.getDate();
    var time = today.getHours() + ":" + today.getMinutes() + ":" + today.getSeconds();
    var dateTime = date+' '+time;
    var pests = [];
    var messages = [];


    const fileName = body["image"];
    const bucketName = fileName.split("/")[0];
    const imageName = fileName.split("/").slice(1,).join("/");


    const bucket = storage.bucket(bucketName);
    const file = bucket.file(imageName);
    const signedUrls = await file.getSignedUrl({
      action: 'read',
      expires: '03-09-2491'

    });

    var record = {
      title: 'Fungal Disease detected at '+data.station,
      body: body["class"] + ' was detected on '+data.plant+' station-1. '+body["treatment"],
      station: data.station,
      plant: data.plant,
      image: body["image"],
      timestamp: dateTime
    };

    addNotification(record, 'fungal-classify-notifications');
    
    
      console.log(signedUrls[0]);
      var url = signedUrls[0];
      var message = {
        notification: {
          title: 'Fungal Disease detected at '+data.station,
          body: body["class"] + ' was detected on '+data.plant+' station-1. '+body["treatment"]
        },
        android: {
          notification: {
            imageUrl: url
          }
        },
        apns: {
          payload: {
            aps: {
              'mutable-content': 1
            }
          },
          fcm_options: {
            image: url
          }
        },
        webpush: {
          headers: {
            image: url
          }
        }
      };
      
    

    return message;
}


async function getGrowthNotification(body, data)
{
    console.log(body);
    console.log(Object.keys(body));
    var today = new Date();
    var date = today.getFullYear()+'-'+(today.getMonth()+1)+'-'+today.getDate();
    var time = today.getHours() + ":" + today.getMinutes() + ":" + today.getSeconds();
    var dateTime = date+' '+time;
    var pests = [];
    var messages = [];


    const fileName = body["image"];
    const bucketName = fileName.split("/")[0];
    const imageName = fileName.split("/").slice(1,).join("/");


    const bucket = storage.bucket(bucketName);
    const file = bucket.file(imageName);
    const signedUrls = await file.getSignedUrl({
      action: 'read',
      expires: '03-09-2491'

    });

    var record = {
      title: 'Plant Growth Alert at '+data.station + ' for '+data.plant,
      body: body['treatment'],
      station: data.station,
      plant: data.plant,
      image: body["image"],
      timestamp: dateTime
    };

    addNotification(record, 'plant-growth-notifications');
    
      console.log(signedUrls[0]);
      var url = signedUrls[0];
      var message = {
        notification: {
          title: 'Plant Growth Alert at '+data.station + ' for '+data.plant,
          body: body['treatment']
        },
        android: {
          notification: {
            imageUrl: url
          }
        },
        apns: {
          payload: {
            aps: {
              'mutable-content': 1
            }
          },
          fcm_options: {
            image: url
          }
        },
        webpush: {
          headers: {
            image: url
          }
        }
      };
      
    

    return message;
}


async function getThermalNotification(body, data)
{
    console.log(body);
    console.log(Object.keys(body));
    var today = new Date();
    var date = today.getFullYear()+'-'+(today.getMonth()+1)+'-'+today.getDate();
    var time = today.getHours() + ":" + today.getMinutes() + ":" + today.getSeconds();
    var dateTime = date+' '+time;
    var pests = [];
    var messages = [];


    const fileName = body["image"];
    const bucketName = fileName.split("/")[0];
    const imageName = fileName.split("/").slice(1,).join("/");


    const bucket = storage.bucket(bucketName);
    const file = bucket.file(imageName);
    const signedUrls = await file.getSignedUrl({
      action: 'read',
      expires: '03-09-2491'

    });

    var record = {
      title: 'Thermal Analysis Alert at '+data.station + ' for '+data.plant,
      body: 'The Mean Temperature is '+body['mean_temperature']+'.'+body['treatment'],
      station: data.station,
      plant: data.plant,
      image: body["image"],
      timestamp: dateTime
    };

    result = await addNotification(record, 'thermal-notifications');
    console.log(result);

    
    
      console.log(signedUrls[0]);
      var url = signedUrls[0];
      var message = {
        notification: {
          title: 'Thermal Analysis Alert at '+data.station + ' for '+data.plant,
          body: 'The Mean Temperature is '+body['mean_temperature']+'.'+body['treatment']
        },
        android: {
          notification: {
            imageUrl: url
          }
        },
        apns: {
          payload: {
            aps: {
              'mutable-content': 1
            }
          },
          fcm_options: {
            image: url
          }
        },
        webpush: {
          headers: {
            image: url
          }
        }
      };
      
    

    return message;
}











app.get('/fetch',(req,resp) => {
    (async() => {

        console.log("Fetching data for MongoDB");
        var data = await loadDB();
        ImagePath = data.imagePath;
        PlantType = data.plantType;
        apitype = data.apiType;
        CustomerDb = data.customerdb;
        HostIP = data.HostIP;
        console.log("Fetched the required values");

        resp.send(data)

      })();
    
});


app.get('/thermal', function(req, res) {
    (async() => {

        console.log("Thermal EndPoint Activated");
        var url = await thermal();
        console.log("Thermal URL created");

        request(url, function (error, response, body) {
            console.error('error:', error); 
            console.log('statusCode:', response && response.statusCode); 
            console.log('body:', body); 
            res.send(body);
          });

      })();
    
});


app.get('/v1/growth',(req,res) => {
    (async() => {

        console.log("PlantGrowth EndPoint Activated");
        var url = await growth();
        console.log("PlantGrowth URL created");

        request(url[0], function (error, response, body) {
            console.error('error:', error); 
            console.log('statusCode:', response && response.statusCode); 

            body = JSON.parse(body);
            if('state' in body)
              {
                if(body['state'] == 'Unhealthy')
                {
                  request(url[0], function (error, response, body) {
                    console.error('error:', error); 
                    console.log('statusCode:', response && response.statusCode); 
                    console.log('body:', body);    
                    body = JSON.parse(body);
                      console.log('Inside');
                      getGrowthNotification(body,url[1]).then(notification => {
                        console.log(notification);
                        var result = sendNotification(notification);
                        console.log(notification);
                      
                      });
                    
                    
                    res.send(body);
                  });
          
                }
              }

          });

      })();
})

app.get('/v1/thermal',(req,res) => {
  (async() => {

      console.log("ThermalAnalysis EndPoint Activated");
      var url = await thermal();
      console.log("ThermalAnalysis URL created");

      request(url[0], function (error, response, body) {
          console.error('error:', error); 
          console.log('statusCode:', response && response.statusCode); 

          body = JSON.parse(body);
          console.log(body);
          if('health_status' in body)
            {
              if(body['health_status'] == 'Plant is not healthly')
              {
                request(url[0], function (error, response, body) {
                  console.error('error:', error); 
                  console.log('statusCode:', response && response.statusCode); 
                  console.log('body:', body);    
                  body = JSON.parse(body);
                    console.log('Inside');
                    getThermalNotification(body,url[1]).then(notification => {
                      console.log(notification);
                      var result = sendNotification(notification);
                      console.log(notification);
                    
                    });
                  
                  
                  res.send(body);
                });
        
              }
            }

        });

    })();
})





app.get('/v1/pestdetect', function(req, res) {
    (async() => {

        console.log("Detection EndPoint Activated");
        var url = await detect();
        console.log("Detect URL created");

        request(url[0], function (error, response, body) {
            console.error('error:', error); 
            console.log('statusCode:', response && response.statusCode); 
            console.log('body:', body); 
      
            getDetectNotification(JSON.parse(body),url[1]).then(notifications => {
              console.log(notifications);
            for(var i=0;i<notifications.length;i++)
            {
              var result = sendNotification(notifications[i]);
              console.log(notifications[i]);
            }
            
            });
            
            //console.log('Notification: ',notification);
            res.send(body);
          });

      })();
    
});


app.get('/v1/fungalclassify', function(req, res) {
  (async() => {

      console.log("Classification EndPoint Activated");
      var url = await classify();
      console.log("Classify URL created");

      request(url[0], function (error, response, body) {
          console.error('error:', error); 
          console.log('statusCode:', response && response.statusCode); 
          console.log('body:', body);    
          body = JSON.parse(body);
          if('treatment' in body)
          {
            console.log('Inside');
            getClassifyNotification(body,url[1]).then(notification => {
              console.log(notification);
              var result = sendNotification(notification);
              console.log(notification);
            
            });
          }
          
          res.send(body);
        });

    })();
  
});



app.listen(PORT, '0.0.0.0',function (){ 
    console.log('Listening on Port 3000');
});  