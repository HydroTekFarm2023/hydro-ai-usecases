var admin = require("firebase-admin");

var serviceAccount = require("./hydrotek-286213-firebase-adminsdk-fxlxp-1ec2464fc0.json");

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount)
});



function sendNotification(message)
  { 
    var db = admin.firestore();
    db.collection('userData').doc('cLEjR4njUPMc0kYuiOZqqP6kVHt1').get().then((snapshot) => {
      const registrationToken = snapshot.get('registrationToken');
      message["token"] = registrationToken;
      admin.messaging().send(message).then((response) => {
          console.log('Successfully sent message:', response);
          return 'Successfully sent message:'+response;
        })
        .catch((error) => {
          console.log('Error sending message:', error);
          return 'Error Sending message: '+error;
        });
    
    })

       
  }

  module.exports = sendNotification;