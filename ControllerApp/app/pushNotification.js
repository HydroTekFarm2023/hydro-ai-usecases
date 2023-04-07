var admin = require("firebase-admin");

var serviceAccount = require("./hydrotek-internship-firebase-adminsdk-19v3r-3d17759ddc.json");

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount)
});



const notification_options = {
    priority: "high",
    timeToLive: 60 * 60 * 24
  };
const  registrationToken = 'fVt2XP1CQyiQcA7mEj97j6:APA91bG0wVXLbMESK27xKhP6WJAmW5Eyc0w0aSelFZsKR1x5WQHSiFzEyeNZRbBLKCzfqR8yA3WTiQ6t7A5YTSmfxv1rBParz_v29HbZcKq2UvO5f7FW2sjJrWWm_EHhgywIFOaa-U2G'
const topicName = "Hydrotek"
const message = {
    notification: {
      title: 'Sparky says hello!'
    },
    android: {
      notification: {
        imageUrl: 'https://foo.bar.pizza-monster.png'
      }
    },
    apns: {
      payload: {
        aps: {
          'mutable-content': 1
        }
      },
      fcm_options: {
        image: 'https://foo.bar.pizza-monster.png'
      }
    },
    webpush: {
      headers: {
        image: 'https://foo.bar.pizza-monster.png'
      }
    },
    token: registrationToken
  };
  
const options =  notification_options
    
admin.messaging().send(message).then((response) => {
    // Response is a message ID string.
    console.log('Successfully sent message:', response);
  })
  .catch((error) => {
    console.log('Error sending message:', error);
  });

  async function sendNotification(message)
  {
    admin.messaging().send(message).then((response) => {
        // Response is a message ID string.
        console.log('Successfully sent message:', response);
      })
      .catch((error) => {
        console.log('Error sending message:', error);
      });
     
  }