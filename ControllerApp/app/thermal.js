const request = require('request');
const loadDB = require('./database');

async function thermal() {

    console.log("Fetched the data");

    //var data = await loadDB();
    //let imageName = data.imageid;
    let plant = "lettuce";
    let station = "hydrotek-farm";
    let ImagePath = "hydrotekai/thermal_images/cropped_leaf.jpg";
    let X = 9;
    let Y = 10;
    let Height = 170;
    let Width = 201;
    let PlantType = 'lettuce';
    
    let apitype = "devtest";
    let CustomerDb = "hydrotek";

    let hostName = '35.226.53.51';
    let portNo = '6005';

   
    let thermal_call = 'http://'+hostName+':'+portNo+'/thermalanalysis?ImagePath='+ImagePath+'&X='+X+'&Y='+Y+'&Height='+Height+'&Width='+Width+'&PlantType='+PlantType+'&apitype='+apitype+'&CustomerDb='+CustomerDb;


    console.log(thermal_call);
    console.log("Returned the Thermal call URL");

    return [thermal_call,{"station":station, "plant": plant}];
  
}

module.exports = thermal;

// (async() => {
      
//   var url = await detect();
//   request(url, function (error, response, body) {
//     console.error('error:', error); // Print the error
//     console.log('statusCode:', response && response.statusCode); // Print the response status code if a response was received
//     console.log('body:', body); // Print the data received
//     return body; //Display the response on the website
//   });
// })();