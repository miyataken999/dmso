import React, { Component } from "react";
import { StyleSheet, View, TextInput } from "react-native";
import Icon from "react-native-vector-icons/EvilIcons";

function Index(props) {
  return (
    <View style={styles.container}>
      <Icon name="search" style={styles.searchIcon}></Icon>
      <TextInput placeholder="Search" style={styles.searchInput}></TextInput>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: "#1a1a1c",
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "flex-start",
    borderRadius: 10,
    width: 273,
    height: 40
  },
  searchIcon: {
    color: "grey",
    fontSize: 20,
    marginLeft: 5,
    marginRight: 1
  },
  searchInput: {
    width: 239,
    height: 40,
    color: "rgba(255,255,255,1)",
    marginRight: 1,
    marginLeft: 5,
    fontSize: 14,
    fontFamily: "ibm-plex-sans-regular"
  }
});

export default Index;
