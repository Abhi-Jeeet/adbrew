/**
 * todoApi.js
 * ----------
 * Thin service layer that encapsulates all HTTP calls to the Django backend.
 * Keeping API calls in one place follows the Single Responsibility Principle
 * and makes it trivial to swap the base URL or add auth headers later.
 */

const BASE_URL = "http://localhost:8000";

/**
 * Fetch all todos from the backend.
 * @returns {Promise<Array>} Resolves with an array of todo objects.
 */
export async function fetchTodos() {
  const response = await fetch(`${BASE_URL}/todos/`);
  if (!response.ok) {
    throw new Error(`GET /todos failed – ${response.status} ${response.statusText}`);
  }
  const data = await response.json();
  return data.todos;
}

/**
 * Create a new todo on the backend.
 * @param {string} description - The todo description text.
 * @returns {Promise<Object>} Resolves with the created todo object.
 */
export async function createTodo(description) {
  const response = await fetch(`${BASE_URL}/todos/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ description }),
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(
      errorData.error || `POST /todos failed – ${response.status} ${response.statusText}`
    );
  }
  const data = await response.json();
  return data.todo;
}
