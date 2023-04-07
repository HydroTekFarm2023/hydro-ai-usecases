const request = require('request');
const loadDB = require('./database');

async function detect() {

    console.log("Fetched the data");

    var data = await loadDB();
    //let imageName = data.imageid;
    let imageName = "t3.jpg";
    let source = data.source;
    let dest = data.dest;
    let plant = "lettuce";
    let station = "hydrotek-farm";

    let hostName = '35.193.229.177';
    let portNo = '5001';

    let detect_call = 'http://'+hostName+':'+portNo+'/v1/pestdetection/treatment?source='+source+'&imageName='+imageName+'&dest='+dest;

    
    console.log("Returned the Detect call URL");

    return [detect_call,{"station":station, "plant": plant}];
  
}

module.exports = detect;

// (async() => {
      
//   var url = await detect();
//   request(url, function (error, response, body) {
//     console.error('error:', error); // Print the error
//     console.log('statusCode:', response && response.statusCode); // Print the response status code if a response was received
//     console.log('body:', body); // Print the data received
//     return body; //Display the response on the website
//   });
// })();