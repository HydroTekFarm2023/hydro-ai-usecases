const MongoClient = require('mongodb').MongoClient;

const url = "mongodb+srv://hydrotek-user:admin@cluster0.rnfsf.mongodb.net/myFirstDatabase?retryWrites=true&w=majority";


async function findOne() {

    const client = await MongoClient.connect(url, { useNewUrlParser: true })
        .catch(err => { console.log(err); });

    if (!client) {
        return;
    }

    try {

        const db = client.db("hydrotek");

        let collection = db.collection('images');

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

