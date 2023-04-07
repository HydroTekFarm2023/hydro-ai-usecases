const MongoClient = require('mongodb').MongoClient;

//const url = "mongodb+srv://hydrotek-user:admin@cluster0.rnfsf.mongodb.net/myFirstDatabase?retryWrites=true&w=majority";

var username = (process.env.MONGO_USER === undefined) ? 'hydrotekai' : process.env.MONGO_USER;
var pwd = (process.env.MONGO_PWD === undefined) ? 'Kansas2020!m' : process.env.MONGO_PWD;
var host = (process.env.MONGO_USER === undefined) ? 'cluster0.x5wba.gcp.mongodb.net' : process.env.MONGO_HOST;
var mongocmd = "mongodb+srv://"+username+":"+pwd+"@" + host + "/" + 'hydrotek' + "?retryWrites=false"

async function addNotification(notification, collection_name) {

    const client = await MongoClient.connect(mongocmd, { useNewUrlParser: true })
        .catch(err => { console.log(err); });

    if (!client) {
        return;
    }

    try {

        const db = client.db("pushnotification");

        let collection = db.collection(collection_name);
        let result = await collection.insertOne(notification);
        console.log("Added notification to "+collection_name);

        //let query = { name: 'Volkswagen' }

 
        return result;

    } catch (err) {

        console.log(err);
    } finally {

        client.close();
    }
}

module.exports = addNotification;

// (async() => {
      
//   var data = await findOne();
//   console.log(data);
// })();

