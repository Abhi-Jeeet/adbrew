/**
 * App.js
 * ------
 * Root component that composes TodoList and TodoForm.
 * State and API calls are managed via the custom `useTodos` hook.
 * No class-based components or lifecycle methods are used – only React hooks.
 */

import React from "react";
import "./App.css";
import { useTodos } from "./hooks/useTodos";
import TodoList from "./components/TodoList";
import TodoForm from "./components/TodoForm";

function App() {
  const { todos, loading, error, addTodo } = useTodos();

  return (
    <div className="App">
      <div className="section">
        <h1>List of TODOs</h1>
        <TodoList todos={todos} loading={loading} error={error} />
      </div>

      <div className="section">
        <h1>Create a ToDo</h1>
        <TodoForm onAdd={addTodo} />
      </div>
    </div>
  );
}

export default App;
