import React from 'react';

import HomeScreen from './screens/HomeScreen'
import ChatScreen from './screens/ChatScreen'

import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
const Stack = createStackNavigator();

export default function Chat() {
  return <NavigationContainer>
      <Stack.Navigator
      initialRouteName="Home"
      screenOptions={{ gestureEnabled: true }}
    >
      <Stack.Screen
        name="Home"
        component={HomeScreen}
      />
      <Stack.Screen
        name="Chat"
        component={ChatScreen}
      />
    </Stack.Navigator>
  </NavigationContainer>;
}