const request = require('request');
const loadDB = require('./database');

async function growth() {

    console.log("Fetched the data");

    //var data = await loadDB();
    //let imageName = data.imageid;
    let plant = "lettuce";
    let station = "hydrotek-farm";
    let plantAge = 4;
    let ImagePath = "hydrotekai/HeightAnalysis/NFTtest2.jpg";
    let system = "NFT";
    let PlantId = "1";
    let apitype = "devtest";
    let CustomerDb = "hydrotek";

    let hostName = '34.71.125.6';
    let portNo = '6003';

    let growth_call = 'http://'+hostName+':'+portNo+'/PlantGrowth?ImagePath='+ImagePath+'&system='+system+'&PlantId='+PlantId+'&apitype='+apitype+'&CustomerDb='+CustomerDb;


    console.log(growth_call);
    console.log("Returned the Detect call URL");

    return [growth_call,{"station":station, "plant": plant, "plantAge": plantAge}];
  
}

module.exports = growth;

// (async() => {
      
//   var url = await detect();
//   request(url, function (error, response, body) {
//     console.error('error:', error); // Print the error
//     console.log('statusCode:', response && response.statusCode); // Print the response status code if a response was received
//     console.log('body:', body); // Print the data received
//     return body; //Display the response on the website
//   });
// })();