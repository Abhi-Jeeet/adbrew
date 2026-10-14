/**
 * useTodos.js
 * -----------
 * Custom React hook that owns the todos state and exposes a clean API:
 *   - todos        : current list of todos
 *   - loading      : true while fetching from the backend
 *   - error        : string message when something goes wrong (or null)
 *   - refreshTodos : function to manually re-fetch
 *   - addTodo      : function to create a new todo and refresh the list
 */

import { useState, useEffect, useCallback } from "react";
import { fetchTodos, createTodo } from "../api/todoApi";

export function useTodos() {
  const [todos, setTodos] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const refreshTodos = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchTodos();
      setTodos(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch todos on initial mount
  useEffect(() => {
    refreshTodos();
  }, [refreshTodos]);

  const addTodo = useCallback(
    async (description) => {
      await createTodo(description);
      await refreshTodos();
    },
    [refreshTodos]
  );

  return { todos, loading, error, refreshTodos, addTodo };
}
