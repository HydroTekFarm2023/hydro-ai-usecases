const request = require('request');
const loadDB = require('./database');

async function thermal() {

    console.log("Fetched the data");

    var data = await loadDB();
    let ImagePath = data.imagePath;
    let PlantType = data.plantType;
    let apitype = data.apiType;
    let CustomerDb = data.customerdb;
    let HostIP = data.HostIP;

    let thermal_call = 'http://34.133.172.57:6005/thermalanalysis?ImagePath=' + ImagePath + '&X=9&Y=10&Height=170&Width=201&Threshold=20&PlantType=' + PlantType + '&apitype=' + apitype + '&CustomerDb=' + CustomerDb + '&HostIP=' + HostIP;

    console.log("Returned the Thermal call URL");

    return thermal_call;
  
}

module.exports = thermal;

// (async() => {
      
//   var url = await thermal();
//   request(url, function (error, response, body) {
//     console.error('error:', error); // Print the error
//     console.log('statusCode:', response && response.statusCode); // Print the response status code if a response was received
//     console.log('body:', body); // Print the data received
//     return body; //Display the response on the website
//   });
// })();