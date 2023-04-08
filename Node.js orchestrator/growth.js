const request = require('request');
const loadDB = require('./database');

async function growth() {

    console.log("Fetched the data");

    var data = await loadDB();
    let ImagePath = data.imagePath;
    let PlantID = data.plantId;
    let apitype = data.apiType;
    let system = data.system;
    let CustomerDb = data.customerdb;

    let growth_call = 'http://34.121.87.6:6003/PlantGrowth?ImagePath=' + ImagePath + '&system=' + system + '&PlantId=' + PlantID + '&apitype=' + apitype + '&CustomerDb=' + CustomerDb;

    console.log("Returned the Plant Growth call URL");

    return growth_call;
  
}

module.exports = growth;

// (async() => {
      
//   var url = await growth();
//   console.log(url);
//   request(url, function (error, response, body) {
//     console.error('error:', error); // Print the error
//     console.log('statusCode:', response && response.statusCode); // Print the response status code if a response was received
//     console.log('body:', body); // Print the data received
//     return body; //Display the response on the website
//   });
// })();