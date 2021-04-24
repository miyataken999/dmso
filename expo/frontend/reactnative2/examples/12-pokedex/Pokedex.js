import React,{Component,useEffect, useReducer, useState } from "react";
import { Alert, Modal, Button, Platform, View, Text, Image, TouchableHighlight } from "react-native";
import { StatusBar } from "expo-status-bar";
import { NavigationContainer } from "@react-navigation/native";
import { createStackNavigator } from "@react-navigation/stack";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";

import PokemonList from "./screens/PokemonList";
import MoveList from "./screens/MoveList";
import PokemonDetail from "./screens/PokemonDetail";
import MoveDetail from "./screens/MoveDetail";

import pokemonTabIcon from "../../assets/pokedex/pokemon-active.png";
import moveTabIcon from "../../assets/pokedex/move-active.png";
import Appl from "./Appl"

import HelloWorld1 from "../1-hello-world/1.HelloWorld1";
import HelloWorld2 from "../1-hello-world/2.HelloWorld2";
import MomoLogin from "../2-login-screen/1.MomoLogin";
import FacebookLogin from "../2-login-screen/2.FacebookLogin";
import TheLight from "../3-the-light/1.TheLight";
import TrafficLight from "../3-the-light/2.TrafficLight";
import RegisterForm from "../4-register-form/RegisterForm";
import InstagramFeed from "../5-instagram-feed/InstagramFeed";
import RockPaperScissors from "../6-rock-paper-scissors/RockPaperScissors";
import ScanQrCode from "../7-scan-qr-code/ScanQrCode";
import StopWatch from "../8-stopwatch/StopWatch";
import BMICalculator from "../9-bmi-calculator/BMICalculator";
import MusicPlayer from "../10-music-player/MusicPlayer";
import WorldwideNews from "../11-news/WorldwideNews";
//import Appl from "../with-apollo/Appl"
//import Pokedex from "../examples/12-pokedex/Pokedex";
//import Appl from "./examples/with-apollo/Appl"

// https://reactnavigation.org/docs/stack-navigator/
const PokemonStack = createStackNavigator();
const MoveStack = createStackNavigator();
const apploStack = createStackNavigator();
import { createDrawerNavigator } from '@react-navigation/drawer';
//import { NavigationContainer } from '@react-navigation/native';
const Drawer = createDrawerNavigator();
const stackScreenOptions = {
  headerShown: false,
  gestureEnabled: true,
};

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
//json でＳｔａｃｋを作成して動的にすればよい
function PokemonStackScreen() {
  return (
    <PokemonStack.Navigator screenOptions={stackScreenOptions}>
      <PokemonStack.Screen name="PokemonList" component={PokemonList} />
      <PokemonStack.Screen name="PokemonDetail" component={PokemonDetail} />
    </PokemonStack.Navigator>
  );
}

function MoveStackScreen() {
  return (
    <MoveStack.Navigator screenOptions={stackScreenOptions}>
      <MoveStack.Screen name="MoveList" component={MoveList} />
      <MoveStack.Screen name="MoveDetail" component={MoveDetail} />   
    </MoveStack.Navigator>
  );
}

// https://reactnavigation.org/docs/bottom-tab-navigator/
const Tab = createBottomTabNavigator();
const ActiveColor = "#000000";
const InActiveColor = "#00000077";
const tabScreenOptions = ({ route }) => ({
  tabBarIcon: ({ color, size }) => {
    return (
      <View style={{ alignItems: "center" }}>
        <Image
          source={route.name === "Pokemons" ? pokemonTabIcon : moveTabIcon}
          style={{
            opacity: color == ActiveColor ? 1 : 0.5,
            width: size,
            height: size,
          }}
        />
      </View>
    );
  },
});
const tabBarOptions = {
  activeTintColor: ActiveColor,
  inactiveTintColor: InActiveColor,
};

export default class Pokedex extends Component {

  state = {
    modalVisible: false,
  };

  setModalVisible(visible) {
    this.setState({modalVisible: visible});
  }
   render() {
  return (
    
      <NavigationContainer>
        <Modal
          animationType="slide"
          transparent={false}
          visible={this.state.modalVisible}
          onRequestClose={() => {
            Alert.alert('Modal has been closed.');
          }}>
          <View style={{marginTop: 22}}>
            <View>
              <Text>Hello World!</Text>

              <TouchableHighlight
                onPress={() => {
                  this.setModalVisible(!this.state.modalVisible);
                }}>
                <Text>Hide Modal</Text>
              </TouchableHighlight>
            </View>
          </View>
        </Modal>

        <TouchableHighlight
          onPress={() => {
            this.setModalVisible(true);
          }}>
          <Text>Show Modal</Text>
        </TouchableHighlight>
      <Text>aaaaaa</Text>    
        <Tab.Navigator
          screenOptions={tabScreenOptions}
          tabBarOptions={tabBarOptions}
        >      
          <Tab.Screen name="Pokekk4ns" component={PokemonStackScreen} />
          <Tab.Screen name="Pokekkns" component={RegisterForm} />
          <Tab.Screen name="Pokekkns22" component={Appl} />
          <Tab.Screen name="Moves" component={MoveStackScreen} />
        </Tab.Navigator>
      </NavigationContainer>
  );
   }
}
