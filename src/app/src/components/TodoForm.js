/**
 * TodoForm.js
 * -----------
 * Controlled form component for creating a new todo.
 * Uses React hooks (useState) for local form state only.
 * Submitting calls the `onAdd` callback (injected from App) which hits the API.
 */

import React, { useState } from "react";

function TodoForm({ onAdd }) {
  const [description, setDescription] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const trimmed = description.trim();
    if (!trimmed) {
      setFormError("Please enter a todo description.");
      return;
    }

    setSubmitting(true);
    setFormError(null);

    try {
      await onAdd(trimmed);
      setDescription(""); // clear input on success
    } catch (err) {
      setFormError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="todo-form">
      <div className="form-group">
        <label htmlFor="todo">ToDo:</label>
        <input
          id="todo"
          type="text"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="What needs to be done?"
          disabled={submitting}
        />
      </div>
      {formError && <p className="status-msg error">{formError}</p>}
      <div className="form-group">
        <button type="submit" disabled={submitting}>
          {submitting ? "Adding…" : "Add ToDo!"}
        </button>
      </div>
    </form>
  );
}

export default TodoForm;
