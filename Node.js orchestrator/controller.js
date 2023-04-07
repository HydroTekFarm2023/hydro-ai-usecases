const express = require('express');
const MongoClient = require('mongodb').MongoClient;
const request = require('request');
const http = require("http");
const loadDB = require('./database');
const thermal = require('./thermal');
const growth = require('./growth');

const app = express();
app.use(express.json())
const PORT = 3000;

var ImagePath;
var PlantType;
var apitype;
var CustomerDb;
var HostIP;

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


app.get('/growth',(req,res) => {
    (async() => {

        console.log("PlantGrowth EndPoint Activated");
        var url = await growth();
        console.log("PlantGrowth URL created");

        request(url, function (error, response, body) {
            console.error('error:', error); 
            console.log('statusCode:', response && response.statusCode); 
            console.log('body:', body); 
            res.send(body);
          });

      })();
})


app.get('/fungal',(req,resp) => {
    console.log("Calling Fungal API")
    resp.send("Calling Fungal api") 
})


app.get('/pest',(req,resp) => {
    console.log("Calling pest API")
    resp.send("Calling pest api") 
})


app.listen(PORT, function (){ 
    console.log('Listening on Port 3000');
});  