/**
 * TodoList.js
 * -----------
 * Presentational component: renders the list of todos fetched from the backend.
 */

import React from "react";

function TodoList({ todos, loading, error }) {
  if (loading) {
    return <p className="status-msg">Loading todos…</p>;
  }

  if (error) {
    return <p className="status-msg error">Error: {error}</p>;
  }

  if (todos.length === 0) {
    return <p className="status-msg">No todos yet. Add one below!</p>;
  }

  return (
    <ul className="todo-list">
      {todos.map((todo) => (
        <li key={todo.id} className="todo-item">
          {todo.description}
        </li>
      ))}
    </ul>
  );
}

export default TodoList;
