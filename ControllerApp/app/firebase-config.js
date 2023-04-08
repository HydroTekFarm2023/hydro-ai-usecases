var admin = require("firebase-admin");

var serviceAccount = require("./hydrotek-internship-firebase-adminsdk-19v3r-3d17759ddc.json");

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount)
});


module.exports.admin = admin