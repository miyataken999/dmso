import React, { useState } from 'react';
import { Button, Text, View, SafeAreaView, ActivityIndicator, StyleSheet } from 'react-native';
//import { ApolloProvider, useQuery, gql } from '@apollo/client';
import { Picker } from '@react-native-picker/picker';
import { NavigationContainer } from "@react-navigation/native";
import { createStackNavigator } from "@react-navigation/stack";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import gql from 'graphql-tag';
import { ApolloClient } from 'apollo-client';
import { InMemoryCache } from 'apollo-cache-inmemory';
import { createHttpLink } from 'apollo-link-http';
import { ApolloProvider,useQuery } from "react-apollo";

import { apolloClient } from './apollo';

const PokemonStack = createStackNavigator();
const MoveStack = createStackNavigator();
const apploStack = createStackNavigator();
const stackScreenOptions = {
  headerShown: false,
  gestureEnabled: true,
};

function PokemonStackScreen() {
  return (
    <PokemonStack.Navigator screenOptions={stackScreenOptions}>
      <PokemonStack.Screen name="PokemonList" component={PokemonList} />
      <PokemonStack.Screen name="PokemonDetail" component={PokemonDetail} />
    </PokemonStack.Navigator>
  );
}

// Imperial I-class Star Destroyer
const defaultStarshipId = 'c3RhcnNoaXBzOjM=';

const LIST_STARSHIPTS = gql`
  query listStarships {
    allStarships {
      starships {
        id
        name
      }
    }
  }
`;

const GET_STARSHIP = gql`
  query getStarship($id: ID!) {
    starship(id: $id) {
      id
      name
      model
      starshipClass
      manufacturers
      length
      crew
      costInCredits
      consumables
      filmConnection {
        films {
          id
          title
        }
      }
    }
  }
`;

function RootComponent(props) {
  console.log(defaultStarshipId);
  const [starshipId, setStarshipId] = useState(defaultStarshipId);
  const { data, error, loading } = useQuery(GET_STARSHIP, {
    variables: { id: starshipId },
  });

  if (error) { console.log('Error fetching starship', error); }
//set onstathipchent setstate
  return (
    <View style={styles.container}>
      <View style={styles.section}>
        <StarshipPicker
          starshipId={starshipId}
          onStarshipChange={setStarshipId}
        />
      </View>
      {loading ? (
        <ActivityIndicator color='#333' />
      ) : (
        <StarshipDetails starship={data.starship} />
      )}
    </View>
  );
}

function StarshipPicker(props) {
  //graphqlでデータ取得
  const { data, error, loading } = useQuery(LIST_STARSHIPTS);
  console.log(data);

  if (error) { console.log('Error listing starships', error) }
  if (loading) return null;

  const { starships } = data.allStarships;
  console.log(starships)
//pickerの表示
  return (
    <Picker
      selectedValue={props.starshipId}
      onValueChange={props.onStarshipChange}
    >
      {starships.map(starship => (
        <Picker.Item key={starship.id} label={starship.name} value={starship.id} />
      ))}
    </Picker>
  )
}

function StarshipDetails({ starship }) {
  console.log(starship)
  return (
    <>
      <View><Text>aaaa</Text></View>
      <View style={styles.section}>
        <Text style={styles.starshipName}>ssssssssssssssssssss{starship.name}</Text>
        <Text style={styles.starshipModel}>{starship.model}</Text>
      </View>

      <View style={styles.section}>
        <Text style={styles.label}>Operational abilities</Text>
        <Text>- {starship.crew} crew members</Text>
        <Text>- {starship.consumables} without restocking</Text>
      </View>

      <View>
        <Text style={styles.label}>Ship attributes</Text>
        <Text>- {starship.length}m long</Text>
        <Text>- {starship.costInCredits} credits</Text>
      </View>

      <View style={styles.section}>
        <Text style={styles.label}>Manufacturers</Text>
        {starship.manufacturers.map(manufacturer => (
          <Text key={manufacturer}>- {manufacturer}</Text>
        ))}
      </View>

      <View style={styles.section}>
        <Text style={styles.label}>Appeared in</Text>
        {starship.filmConnection.films.map(film => (
          <Text key={film.id}>- {film.title}</Text>
        ))}
      </View>
    </>
  )
}

const styles = StyleSheet.create({
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  container: {
    flex: 1,
    justifyContent: 'center',
    paddingHorizontal: 50,
  },
  label: {
    marginBottom: 2,
    fontSize: 12,
    fontWeight: 'bold',
    textTransform: 'uppercase',
  },
  section: {
    marginVertical: 12,
  },
  starshipName: {
    fontSize: 32,
    fontWeight: 'bold',
  },
  starshipModel: {
    fontStyle: 'italic',
  },
});

export default function Appl() {
  return (
    <ApolloProvider client={apolloClient}>
      <RootComponent />
    </ApolloProvider>
  );
}
