import React from 'react';

// firebase https://qiita.com/yukihigasi/items/f93ac7aed7de7c56c16b
import * as firebase from 'firebase';
import 'firebase/firestore';


const firebaseConfig = {
  api:keyとか
};

firebase.initializeApp(firebaseConfig);

//クラス
class Sample extends React.Component {

onStartButtonPress = () => {

      dbh.collection("users").doc("test").set({

      })
}

render() {

    return (

      <View>
    <Button
          title='Firebaseはじめる'
          onPress={this.onStartButtonPress}
           />

      </View>
    );
  }

}
