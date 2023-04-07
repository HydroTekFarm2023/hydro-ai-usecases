const express = require('express')
const MongoClient = require('mongodb').MongoClient
const request = require('request');
const http = require("http");

const app = express();
app.use(express.json())
const PORT = 3000;
const url = "mongodb+srv://hydrotekai:Kansas2020!m@cluster0.x5wba.gcp.mongodb.net/cust101?retryWrites=true&w=majority"


//Connecting to MongoDB
var db
console.log("Connecting to MongoDB")
MongoClient.connect(url, function(err, database) {
    if(err) return console.error(err);
    db = database.db('cust101')
})
console.log("Successfully connected to MongoDB")

//Initializing variables for thermal API
var ImagePath
var PlantType
var apitype
var CustomerDb
var HostIP


app.get('/fetch',(req,resp) => {
    console.log("Fetching data for MongoDB")
    db.collection('cust101-details').find({}).toArray((err,result) => {
        if(err) throw err
        CustomerDb = result[0].customerdb
        ImagePath = result[0].imagePath
        PlantType = result[0].plantType
        apitype = result[0].apiType
        HostIP = result[0].hostIP

        console.log("Fetched Values are:")
        console.log("CustomerDb - ", CustomerDb)
        console.log("ImagePath  ", ImagePath)
        console.log("PlantType - ", PlantType)
        console.log("APItype - ", apitype)
        console.log("HostIP - ", HostIP)

        resp.send(result)
    }) 
})


app.get('/test',(req,resp) => {
    http.get("http://localhost:3000/fetch", resp => {
        let data = "";

        resp.on("data", chunk => {
            data += chunk;
        })

        resp.on("end", () => {
            let url = JSON.parse(data);
            console.log(url);
        });
    })
    .on("error", err => {
        console.log("Error: " + err.message);
    })
    console.log("-----------------------");
    console.log(ImagePath)
    resp.send(test)  
})
 
app.get('/growth',(req,resp) => {
    console.log("Calling Growth API")
    resp.send("Calling growth api") 
})

//ImagePath,PlantType,apitype,CustomerDb,HostIP
//http://34.133.172.57:6005/thermalanalysis?ImagePath=thermal_images/cropped_leaf.jpg&X=9&Y=10&Height=170&Width=201&Threshold=20&PlantType=lettuce&apitype=devtest&CustomerDb=hydrotekaidb&HostIP=34.133.172.57
app.get('/thermal', function(req, res) {
    http.get("http://localhost:3000/fetch", resp => {
        let data = "";

        resp.on("data", chunk => {
            data += chunk;
        })

        resp.on("end", () => {
            let a = JSON.parse(data);
            console.log("Okay now I am printing");
            console.log(a);
        });
    })
    .on("error", err => {
        console.log("Error: " + err.message);
    })
    /*
    fetchendpoint = request('http://localhost:3000/fetch', function (error, response, body) {
        console.log("Updated the variables")
        a = JSON.parse(body)
        return a[0]
    });
    */
    apitype = a[0].apiType
    ImagePath = a[0].imagePath
    PlantType = a[0].plantType
    CustomerDb = a[0].customerdb
    HostIP = a[0].hostIP

    console.log("-------------------")
    console.log(HostIP)
    thermal_endpoint = 'http://34.133.172.57:6005/thermalanalysis?ImagePath=' + ImagePath + '&X=9&Y=10&Height=170&Width=201&Threshold=20&PlantType=' + PlantType + '&apitype=' + apitype + '&CustomerDb=' + CustomerDb + '&HostIP=' + HostIP
    console.log("Thermal API call URL - ", thermal_endpoint)
    request(thermal_endpoint, function (error, response, body) {
        console.error('error:', error); // Print the error
        console.log('statusCode:', response && response.statusCode); // Print the response status code if a response was received
        console.log('body:', body); // Print the data received
        res.send(body); //Display the response on the website
      });      
});

app.listen(PORT, function (){ 
    console.log('Listening on Port 3000');
});  