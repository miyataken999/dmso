import React from "react";
import { Button, View } from 'react-native';
import HelloWorld1 from "./examples/1-hello-world/1.HelloWorld1";
import HelloWorld2 from "./examples/1-hello-world/2.HelloWorld2";
import MomoLogin from "./examples/2-login-screen/1.MomoLogin";
import FacebookLogin from "./examples/2-login-screen/2.FacebookLogin";
import TheLight from "./examples/3-the-light/1.TheLight";
import TrafficLight from "./examples/3-the-light/2.TrafficLight";
import RegisterForm from "./examples/4-register-form/RegisterForm";
import InstagramFeed from "./examples/5-instagram-feed/InstagramFeed";
import RockPaperScissors from "./examples/6-rock-paper-scissors/RockPaperScissors";
import ScanQrCode from "./examples/7-scan-qr-code/ScanQrCode";
import StopWatch from "./examples/8-stopwatch/StopWatch";
import BMICalculator from "./examples/9-bmi-calculator/BMICalculator";
import MusicPlayer from "./examples/10-music-player/MusicPlayer";
import WorldwideNews from "./examples/11-news/WorldwideNews";
import Pokedex from "./examples/12-pokedex/Pokedex";
import Appl from "./examples/with-apollo/Appl"
// snack bar を作成して読み替える
import { createDrawerNavigator } from '@react-navigation/drawer';
import { NavigationContainer } from '@react-navigation/native';
const Drawer = createDrawerNavigator();

function HomeScreen({ navigation }) {
  return (
    <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center' }}>
      <Button
        onPress={() => navigation.navigate('Notifications')}
        title="Go to notifications"
      />
    </View>
  );
}

function NotificationsScreen({ navigation }) {
  return (
    <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center' }}>
      <Button onPress={() => navigation.goBack()} title="Go back homweeee" />
    </View>
  );
}

export default function App() {
  return (
    <NavigationContainer>
      <Drawer.Navigator initialRouteName="Home">
        <Drawer.Screen name="Home" component={HomeScreen} />
        <Drawer.Screen name="Notifications" component={Appl} />
      </Drawer.Navigator>
    </NavigationContainer>
  );
}