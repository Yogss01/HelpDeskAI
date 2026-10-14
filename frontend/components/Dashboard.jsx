
import React, { useEffect, useState } from "react";
import {
  Ticket,
  Clock,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
  MessageSquare,
  UploadCloud,
  ArrowRight,
} from "lucide-react";

const API_URL = "http://127.0.0.1:8000";

function normalizeStatus(status) {
  return String(status || "open")
    .toLowerCase()
    .replace(/[\s-]+/g, "_");
}

function formatDate(dateValue) {
  if (!dateValue) return "Unknown";

  const date = new Date(dateValue);

  return Number.isNaN(date.getTime())
    ? "Unknown"
    : date.toLocaleString();
}

export default function Dashboard({ onNavigate }) {
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadTickets() {
    setLoading(true);
    setError("");

    try {
      const response = await fetch(`${API_URL}/api/tickets`);

      if (!response.ok) {
        throw new Error("Could not load ticket information.");
      }

      const data = await response.json();

      if (!Array.isArray(data)) {
        throw new Error("The server returned an unexpected ticket format.");
      }

      setTickets(data);
    } catch (err) {
      setError(
        err.message ||
          "Could not connect to FastAPI. Check that the backend is running."
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadTickets();
  }, []);

  const openCount = tickets.filter(
    (ticket) => normalizeStatus(ticket.status) === "open"
  ).length;

  const inProgressCount = tickets.filter(
    (ticket) =>
      normalizeStatus(ticket.status) === "in_progress"
  ).length;

  const resolvedCount = tickets.filter(
    (ticket) =>
      ["resolved", "closed"].includes(
        normalizeStatus(ticket.status)
      )
  ).length;

  const recentTickets = [...tickets]
    .sort((a, b) => {
      const dateA = new Date(a.created_at || 0).getTime();
      const dateB = new Date(b.created_at || 0).getTime();

      return (
        (Number.isNaN(dateB) ? 0 : dateB) -
        (Number.isNaN(dateA) ? 0 : dateA)
      );
    })
    .slice(0, 5);

  const stats = [
    {
      label: "Total Tickets",
      value: tickets.length,
      icon: Ticket,
      className: "dashboard-blue",
    },
    {
      label: "Open Tickets",
      value: openCount,
      icon: AlertCircle,
      className: "dashboard-orange",
    },
    {
      label: "In Progress",
      value: inProgressCount,
      icon: Clock,
      className: "dashboard-purple",
    },
    {
      label: "Resolved",
      value: resolvedCount,
      icon: CheckCircle2,
      className: "dashboard-green",
    },
  ];

  return (
    <div className="dashboard">
      <div className="dashboard-heading">
        <div>
          <h2>Support Overview</h2>
          <p>
            Monitor helpdesk activity and support requests.
          </p>
        </div>

        <button
          type="button"
          className="dashboard-refresh"
          onClick={loadTickets}
          disabled={loading}
        >
          <RefreshCw size={16} />
          {loading ? "Loading..." : "Refresh"}
        </button>
      </div>

      {error && (
        <div className="dashboard-error" role="alert">
          <AlertCircle size={18} />
          <div>
            <strong>Unable to load dashboard</strong>
            <p>{error}</p>
          </div>
        </div>
      )}

      <div className="dashboard-stats">
        {stats.map(({ label, value, icon: Icon, className }) => (
          <article className="dashboard-stat" key={label}>
            <div className={`dashboard-stat-icon ${className}`}>
              <Icon size={22} />
            </div>

            <div>
              <p>{label}</p>
              <h3>
                {loading && tickets.length === 0 ? "—" : value}
              </h3>
            </div>
          </article>
        ))}
      </div>

      <section className="dashboard-section">
        <div className="dashboard-section-heading">
          <div>
            <h3>Recent Tickets</h3>
            <p>Your latest support requests</p>
          </div>

          <button
            type="button"
            className="dashboard-text-button"
            onClick={() => onNavigate("tickets")}
          >
            View all <ArrowRight size={16} />
          </button>
        </div>

        {loading ? (
          <p className="dashboard-empty">Loading tickets...</p>
        ) : error ? (
          <p className="dashboard-empty">
            Ticket information is unavailable.
          </p>
        ) : recentTickets.length === 0 ? (
          <div className="dashboard-empty">
            <Ticket size={30} />
            <strong>No tickets yet</strong>
            <p>Create a support ticket to see activity here.</p>
            <button
              type="button"
              onClick={() => onNavigate("tickets")}
            >
              Create a ticket
            </button>
          </div>
        ) : (
          <div className="dashboard-table-wrapper">
            <table className="dashboard-table">
              <thead>
                <tr>
                  <th>Ticket</th>
                  <th>Category</th>
                  <th>Priority</th>
                  <th>Status</th>
                  <th>Created</th>
                </tr>
              </thead>

              <tbody>
                {recentTickets.map((ticket) => (
                  <tr key={ticket.id}>
                    <td>
                      <strong>{ticket.title}</strong>
                      <span className="dashboard-ticket-id">
                        #{ticket.id}
                      </span>
                    </td>
                    <td>{ticket.category || "General"}</td>
                    <td>
                      <span
                        className={`dashboard-badge priority-${String(
                          ticket.priority || "medium"
                        ).toLowerCase()}`}
                      >
                        {ticket.priority || "Medium"}
                      </span>
                    </td>
                    <td>
                      <span
                        className={`dashboard-badge status-${normalizeStatus(
                          ticket.status
                        )}`}
                      >
                        {String(ticket.status || "open").replace(
                          /_/g,
                          " "
                        )}
                      </span>
                    </td>
                    <td>{formatDate(ticket.created_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <section className="dashboard-section">
        <div className="dashboard-section-heading">
          <div>
            <h3>Quick Actions</h3>
            <p>Continue working in your support workspace</p>
          </div>
        </div>

        <div className="dashboard-actions">
          <button
            type="button"
            className="dashboard-action"
            onClick={() => onNavigate("tickets")}
          >
            <Ticket size={22} />
            <span>
              <strong>Manage Tickets</strong>
              <small>Create and update support requests</small>
            </span>
            <ArrowRight size={18} />
          </button>

          <button
            type="button"
            className="dashboard-action"
            onClick={() => onNavigate("chat")}
          >
            <MessageSquare size={22} />
            <span>
              <strong>Open AI Assistant</strong>
              <small>Ask questions about uploaded documents</small>
            </span>
            <ArrowRight size={18} />
          </button>

          <button
            type="button"
            className="dashboard-action"
            onClick={() => onNavigate("upload")}
          >
            <UploadCloud size={22} />
            <span>
              <strong>Knowledge Base</strong>
              <small>Upload and manage support documents</small>
            </span>
            <ArrowRight size={18} />
          </button>
        </div>
      </section>
    </div>
  );
}
