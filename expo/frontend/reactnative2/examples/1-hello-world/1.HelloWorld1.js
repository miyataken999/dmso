import React from 'react';
import {
  StyleSheet,
  Text,
  View,
  StatusBar,
  Platform,
  ScrollView,
  FlatList,
  // 1: TextInputとButtonを削除
  //TextInput,
  //Button,
  KeyboardAvoidingView,
  AsyncStorage,
  TouchableOpacity,
} from 'react-native';
import {
  SearchBar,
  // 2: TextInputとButtonの代わりにreact-native-elementsのInputとButtonを利用
  Input,
  Button,
} from 'react-native-elements'
//import index from "../libs/SearchBa";
// 3: ボタンのアイコンを Feather から利用する
import Icon from 'react-native-vector-icons/Feather';

const STATUSBAR_HEIGHT = Platform.OS == 'ios' ? 20 : StatusBar.currentHeight;
const TODO = "@todoapp.todo"

const TodoItem = (props) => {
  let textStyle = styles.todoItem
  if (props.done === true) {
    textStyle = styles.todoItemDone
  }
  return (
    <TouchableOpacity onPress={props.onTapTodoItem}>
      <Text style={textStyle}>{props.title}</Text>
    </TouchableOpacity>
  )
}

export default class App extends React.Component {

  constructor(props) {
    super(props)
    this.state = {
      todo: [],
      currentIndex: 0,
      inputText: "",
      filterText: "",
    }
  }

  componentDidMount() {
    this.loadTodo()
  }

  loadTodo = async () => {
    try {
      const todoString = await AsyncStorage.getItem(TODO)
      if (todoString) {
        const todo = JSON.parse(todoString)
        const currentIndex = todo.length
        this.setState({todo: todo, currentIndex: currentIndex})
      }
    } catch (e) {
      console.log(e)
    }
  }

  saveTodo = async (todo) => {
    try {
      const todoString = JSON.stringify(todo)
      await AsyncStorage.setItem(TODO, todoString)
    } catch (e) {
      console.log(e)
    }
  }

  onAddItem = () => {
    const title = this.state.inputText
    if (title == "") {
      return
    }
    const index = this.state.currentIndex + 1
    const newTodo = {index: index, title: title, done: false}
    const todo = [...this.state.todo, newTodo]
    this.setState({
      todo: todo,
      currentIndex: index,
      inputText: ""
    })
    this.saveTodo(todo)
  }

  onTapTodoItem = (todoItem) => {
    const todo = this.state.todo
    const index = todo.indexOf(todoItem)
    todoItem.done = !todoItem.done
    todo[index] = todoItem
    this.setState({todo: todo})
    this.saveTodo(todo)
  }

  render() {
    const filterText = this.state.filterText
    let todo = this.state.todo
    if (filterText !== "") {
      todo = todo.filter(t => t.title.includes(filterText))
    }
    const platform = Platform.OS == 'ios' ? 'ios' : 'android'
    return (
      <KeyboardAvoidingView style={styles.container} behavior="padding">
        <SearchBar
          platform={platform}
          cancelButtonTitle="Cancel"
          onChangeText={(text) => this.setState({filterText: text})}
          onClear={() => this.setState({filterText: ""})}
          value={this.state.filterText}
          placeholder="Type filter text"
        />
        <ScrollView style={styles.todolist}>
          <FlatList data={todo}
            extraData={this.state}
            renderItem={({item}) =>
              <TodoItem
                title={item.title}
                done={item.done}
                onTapTodoItem={() => this.onTapTodoItem(item)}
                />
            }
            keyExtractor={(item, index) => "todo_" + item.index}
          />
        </ScrollView>
        <View style={styles.input}>
          { /* 4: InputText を Input に変更 */ }
          <Input
            onChangeText={(text) => this.setState({inputText: text})}
            value={this.state.inputText}
            containerStyle={styles.inputText}
          />
          { /* 5: Button をアイコンのみのボタンにする */ }
          <Button
            icon={
              <Icon
                name='plus'
                size={30}
                color='white'
              />
            }
            title=""
            onPress={this.onAddItem}
            buttonStyle={styles.inputButton}
          />
        </View>
      </KeyboardAvoidingView>
    );
  }
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    paddingTop: STATUSBAR_HEIGHT,
  },
  todolist: {
    flex: 1
  },
  // 6: inputの高さ調整とボタンの配置位置の調整のためpaddingRightを追加
  input: {
    height: 50,
    flexDirection: 'row',
    paddingRight: 10,
  },
  // 7: テキスト入力欄もpaddingを入れて配置をきれいに
  inputText: {
    paddingLeft: 10,
    paddingRight: 10,
    flex: 1,
  },
  // 8: 円形のボタンを作成するため幅と同じ大きさのborderRadiusを入れる
  inputButton: {
    width: 48,
    height: 48,
    borderWidth: 0,
    borderColor: 'transparent',
    borderRadius: 48,
    backgroundColor: '#ff6347', // ポモドーロを意識してトマト色
  },
  todoItem: {
    fontSize: 20,
    backgroundColor: "white",
  },
  todoItemDone: {
    fontSize: 20,
    backgroundColor: "red",
  },
});