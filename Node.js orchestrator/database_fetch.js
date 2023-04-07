const MongoClient = require('mongodb').MongoClient;

const url = "mongodb+srv://hydrotekai:Kansas2020!m@cluster0.x5wba.gcp.mongodb.net/cust101?retryWrites=true&w=majority";

var db;
var ImagePath;
var PlantType;
var apitype;
var CustomerDb;
var HostIP;


console.log("Connecting to MongoDB")
MongoClient.connect(url, function(err, database) {
    if(err) return console.error(err);
    db = database.db('cust101');

    db.collection('cust101-details').find({}).toArray((err,result) => {
        if(err) throw err
        CustomerDb = result[0].customerdb
        ImagePath = result[0].imagePath
        PlantType = result[0].plantType
        apitype = result[0].apiType
        HostIP = result[0].hostIP
        
        console.log("-------------");
        console.log(HostIP);
    }) 
    console.log("++++++++++++++");
    console.log(HostIP);
})
console.log("Successfully connected to MongoDB");


console.log("Fetched Values are:")
console.log("CustomerDb - ", CustomerDb)
console.log("ImagePath  ", ImagePath)
console.log("PlantType - ", PlantType)
console.log("APItype - ", apitype)
console.log("HostIP - ", HostIP)

