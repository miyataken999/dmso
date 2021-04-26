import firebase from 'firebase'; // 4.8.1

class FirebaseStorage {

  constructor() {
    this.init();
    this.observeAuth();
  }

  init = () => {
    if (!firebase.apps.length) {
        firebase.initializeApp({
    apiKey: "AIzaSyCsOjFyAAuFr1CITcnufG-GpZBKpLgUP90",
    authDomain: "rpa999-56929.firebaseapp.com",
    databaseURL: "https://rpa999-56929.firebaseio.com",
    projectId: "rpa999-56929",
    storageBucket: "rpa999-56929.appspot.com",
    messagingSenderId: "155298248089"
      });
    }
  }

  observeAuth = () =>
    firebase.auth().onAuthStateChanged(this.onAuthStateChanged);

  onAuthStateChanged = user => {
    if (!user) {
      try {
        firebase.auth().signInAnonymously();
      } catch ({ message }) {
        alert(message);
      }
    }
  };

  get uid() {
    let message = {
        text:"test",
        user:"ssss",
        timestamp: this.timestamp,
    };
    //this.append(message);
    return (firebase.auth().currentUser || {}).uid;
  }

  get ref() {
    return firebase.database().ref('messages');
  }

  parse = snapshot => {
    const { timestamp: numberStamp, text, user } = snapshot.val();
    const { key: _id } = snapshot;
    const timestamp = new Date(numberStamp);
    const message = {
      _id,
      timestamp,
      text,
      user,
    };
    return message;
  };

  on = callback =>
    this.ref
      .limitToLast(20)
      .on('child_added', snapshot => callback(this.parse(snapshot)));

  get timestamp() {
    return firebase.database.ServerValue.TIMESTAMP;
  }
  
  send = messages => {
    for (let i = 0; i < messages.length; i++) {
      console.log(i);
      const { text, user } = messages[i];
      const message = {
        text,
        user,
        timestamp: this.timestamp,
      };
      this.append(message);
    }
  };

  append = message => this.ref.push(message);

  off() {
    this.ref.off();
  }
}

FirebaseStorage.shared = new FirebaseStorage();
export default FirebaseStorage;
