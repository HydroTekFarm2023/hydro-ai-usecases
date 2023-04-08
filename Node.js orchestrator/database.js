const MongoClient = require('mongodb').MongoClient;

const url = "mongodb+srv://hydrotekai:Kansas2020!m@cluster0.x5wba.gcp.mongodb.net/cust101?retryWrites=true&w=majority";


async function findOne() {

    const client = await MongoClient.connect(url, { useNewUrlParser: true })
        .catch(err => { console.log(err); });

    if (!client) {
        return;
    }

    try {

        const db = client.db("cust101");

        let collection = db.collection('cust101-details');

        //let query = { name: 'Volkswagen' }

        let res = await collection.findOne({});

        console.log(res);

        return res;

    } catch (err) {

        console.log(err);
    } finally {

        client.close();
    }
}

module.exports = findOne;

// (async() => {
      
//   var data = await findOne();
//   console.log(data);
// })();

