import React, { useEffect, useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  ActivityIndicator,
  Image,
} from "react-native";
import { Icon } from "react-native-elements";
import ProgressBar from "react-native-progress/Bar";
import MainHeader from "../components/MainHeader";
import PokemonType from "../components/PokemonType";
import PokemonStatus from "../components/PokemonStatus";
import { BackgroundColor } from "../constants";
import Appl from "../../with-apollo/Appl"

export default function PokemonDetail({ navigation, route }) {
  const [staProgress, setStaProgress] = useState(0);
  const [atkProgress, setAtkProgress] = useState(0);
  const [defProgress, setDefProgress] = useState(0);
  const [cpProgress, setCpProgress] = useState(0);

  const maxSTA = 400;
  const maxATK = 400;
  const maxDEF = 400;
  const maxCP = 4000;

  const { pokemon = {} } = route.params;
  const key = route.key;
  console.log("===================="+route.key)
  console.log(pokemon)
  const pokemonTypes = pokemon.field_pokemon_type.split(", ");

  const PokemonTypeElement = pokemonTypes.map((type, index) => {
    return (
      <View style={styles.pokemonType} key={index}>
        <PokemonType type={type} />
        <Text>{type.toUpperCase()}</Text>
      </View>
    );
  });

  useEffect(() => {
    const timeOut = setTimeout(() => {
      setStaProgress(+pokemon.sta / maxSTA);
      setAtkProgress(+pokemon.atk / maxATK);
      setDefProgress(+pokemon.def / maxDEF);
      setCpProgress(+pokemon.cp / maxCP);
    }, 800);

    // https://reactjs.org/docs/hooks-effect.html#effects-with-cleanup
    return () => {
      clearTimeout(timeOut);
    };
  }, []);

  return (
    <>
    <View style={styles.container}>
     <MainHeader navigation={navigation} />
     {key !== "PokemonDetail-aFkagQfKhdcWt-A_DQ59L" ? (
        <Appl />
      ) : (
        

      <ScrollView style={{ flex: 1 }}>
        <View style={styles.content}>
          <Image
            style={styles.avatar}
            placeholderStyle={{ backgroundColor: "transparent" }}
            PlaceholderContent={<ActivityIndicator />}
            source={{ uri: pokemon.uri }}
          />

          <Text style={styles.pokemonName}>{pokemon.title_1}</Text>

          <View style={{ flexDirection: "row", justifyContent: "center" }}>
            {PokemonTypeElement}
          </View>

          <View>
            <Text style={styles.description}>
              {pokemon.title_1} is a pokemon {pokemon.field_pokemon_generation}.
              {"\n"}
              Capture Rate: {pokemon.catch_rate}, Flee Rate:{" "}
              {pokemon.field_flee_rate}
            </Text>
          </View>

          <View>
            <PokemonStatus
              title="STA"
              value={pokemon.sta}
              progress={staProgress}
            />

            <PokemonStatus
              title="ATK"
              value={pokemon.atk}
              progress={atkProgress}
            />

            <PokemonStatus
              title="DEF"
              value={pokemon.def}
              progress={defProgress}
            />

            <PokemonStatus
              title="CP"
              value={pokemon.cp}
              progress={cpProgress}
            />
          </View>
        </View>
      </ScrollView>
      )}
    </View>
    </>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: BackgroundColor,
    flex: 1,
  },
  content: {
    flex: 1,
    backgroundColor: "#fff",
    borderRadius: 50,
    padding: 20,
    minHeight: 500,
    marginTop: 150,
    marginBottom: 30,
  },
  avatar: {
    position: "absolute",
    width: 200,
    height: 200,
    alignSelf: "center",
    top: -130,
    resizeMode: "contain",
  },
  pokemonName: {
    marginTop: 80,
    alignSelf: "center",
    fontSize: 30,
    color: "#4f4f4f",
  },
  description: {
    color: "#4f4f4f",
    textAlign: "center",
    lineHeight: 22,
    marginTop: 15,
    marginBottom: 35,
  },
  pokemonType: {
    alignItems: "center",
    paddingLeft: 10,
    paddingRight: 10,
  },
});
