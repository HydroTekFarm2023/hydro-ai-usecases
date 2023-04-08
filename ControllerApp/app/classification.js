const request = require('request');
const loadDB = require('./database');

async function classify() {

    console.log("Fetched the data");

    var data = await loadDB();
    //let imageName = data.imageid;
    let imageName = "tomato-11.jpeg";
    let source = data.source;
    let dest = data.dest;
    let plant = "tomato";
    let station = "hydrotek-farm";
    let model_name = "tomato";
    let model_path = "hydrotek-2022/fungal-models";

    let hostName = '35.188.146.244';
    let portNo = '5001';

    let classify_call = 'http://'+hostName+':'+portNo+'/v1/fungalclassification/treatment?imageName='+imageName+'&source='+source+'&model_name='+model_name+'&model_path='+model_path+'&dest='+dest;

    
    console.log("Returned the Classify call URL");

    return [classify_call,{"station":station, "plant": plant}];
  
}

module.exports = classify;

// (async() => {
      
//   var url = await detect();
//   request(url, function (error, response, body) {
//     console.error('error:', error); // Print the error
//     console.log('statusCode:', response && response.statusCode); // Print the response status code if a response was received
//     console.log('body:', body); // Print the data received
//     return body; //Display the response on the website
//   });
// })();