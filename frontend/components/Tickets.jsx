
import React, { useEffect, useState } from "react";

const API_URL = "http://127.0.0.1:8000";

export default function Tickets() {
  const [tickets, setTickets] = useState([]);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState("general");
  const [priority, setPriority] = useState("medium");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  // Load existing tickets from the backend
  async function loadTickets() {
    try {
      const response = await fetch(`${API_URL}/api/tickets`);

      if (!response.ok) {
        throw new Error("Could not load tickets.");
      }

      const data = await response.json();
      setTickets(data);
      setError("");
    } catch (err) {
      setError(
        "Could not connect to the backend. Make sure FastAPI is running."
      );
    }
  }

  // Load tickets when the component opens
  useEffect(() => {
    loadTickets();
  }, []);

  // Create a new support ticket
  async function handleSubmit(event) {
    event.preventDefault();

    setLoading(true);
    setError("");
    setMessage("");

    try {
      const response = await fetch(`${API_URL}/api/tickets`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          title: title.trim(),
          description: description.trim(),
          category,
          priority,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail
            ? JSON.stringify(data.detail)
            : "Could not create the ticket."
        );
      }

      setTickets((previousTickets) => [
        data,
        ...previousTickets,
      ]);

      setTitle("");
      setDescription("");
      setCategory("general");
      setPriority("medium");
      setMessage("Ticket created successfully.");
    } catch (err) {
      setError(err.message || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  // Update an existing ticket's status
  async function handleStatusChange(ticketId, newStatus) {
    setError("");
    setMessage("");

    try {
      const response = await fetch(
        `${API_URL}/api/tickets/${ticketId}`,
        {
          method: "PATCH",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            status: newStatus,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Could not update ticket status."
        );
      }

      // Update the ticket displayed on the webpage
      setTickets((previousTickets) =>
        previousTickets.map((ticket) =>
          ticket.id === ticketId ? data : ticket
        )
      );

      setMessage("Ticket status updated successfully.");
    } catch (err) {
      setError(
        err.message || "Could not update ticket status."
      );

      // Reload tickets if the update fails
      await loadTickets();
    }
  }

  return (
    <div className="panel">
      <h3>Create Support Ticket</h3>

      <p>
        Describe your issue so the support team can help you.
      </p>

      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="ticket-title">Title</label>

          <input
            id="ticket-title"
            type="text"
            value={title}
            onChange={(event) => setTitle(event.target.value)}
            placeholder="Example: Unable to log in"
            minLength={3}
            maxLength={200}
            required
          />
        </div>

        <div>
          <label htmlFor="ticket-description">
            Description
          </label>

          <textarea
            id="ticket-description"
            value={description}
            onChange={(event) =>
              setDescription(event.target.value)
            }
            placeholder="Explain the problem you are facing"
            minLength={3}
            maxLength={5000}
            rows={4}
            required
          />
        </div>

        <div>
          <label htmlFor="ticket-category">Category</label>

          <select
            id="ticket-category"
            value={category}
            onChange={(event) =>
              setCategory(event.target.value)
            }
          >
            <option value="account">Account</option>
            <option value="billing">Billing</option>
            <option value="technical">Technical</option>
            <option value="general">General</option>
          </select>
        </div>

        <div>
          <label htmlFor="ticket-priority">Priority</label>

          <select
            id="ticket-priority"
            value={priority}
            onChange={(event) =>
              setPriority(event.target.value)
            }
          >
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
        </div>

        <button type="submit" disabled={loading}>
          {loading ? "Creating..." : "Create Ticket"}
        </button>
      </form>

      {message && <p role="status">{message}</p>}
      {error && <p role="alert">{error}</p>}

      <hr />

      <h3>Existing Tickets</h3>

      {tickets.length === 0 ? (
        <p>No tickets found yet.</p>
      ) : (
        <div>
          {tickets.map((ticket) => (
            <article
              key={ticket.id}
              className="panel"
            >
              <h4>{ticket.title}</h4>

              <p>{ticket.description}</p>

              <p>
                <strong>Category:</strong> {ticket.category}
              </p>

              <p>
                <strong>Priority:</strong> {ticket.priority}
              </p>

              <div>
                <label htmlFor={`status-${ticket.id}`}>
                  <strong>Status:</strong>
                </label>

                <select
                  id={`status-${ticket.id}`}
                  value={ticket.status}
                  onChange={(event) =>
                    handleStatusChange(
                      ticket.id,
                      event.target.value
                    )
                  }
                >
                  <option value="open">Open</option>
                  <option value="in_progress">
                    In Progress
                  </option>
                  <option value="resolved">Resolved</option>
                </select>
              </div>

              <p className="muted">
                Created:{" "}
                {ticket.created_at
                  ? new Date(
                      ticket.created_at
                    ).toLocaleString()
                  : "Unknown"}
              </p>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
