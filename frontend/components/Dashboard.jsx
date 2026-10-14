
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
  CreditCard,
  Wrench,
  Users,
  HelpCircle,
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
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadTickets() {
    setLoading(true);
    setError("");

    const errors = [];

    // Load the ticket list.
    try {
      const response = await fetch(`${API_URL}/api/tickets`);

      if (!response.ok) {
        throw new Error("Could not load ticket information.");
      }

      const data = await response.json();

      if (!Array.isArray(data)) {
        throw new Error(
          "The server returned an unexpected ticket format."
        );
      }

      setTickets(data);
    } catch (err) {
      errors.push(
        err.message ||
          "Could not connect to FastAPI. Check that the backend is running."
      );
    }

    // Load analytics from the backend.
    try {
      const response = await fetch(`${API_URL}/api/analytics`);

      if (!response.ok) {
        throw new Error("Could not load ticket analytics.");
      }

      const data = await response.json();

      if (
        typeof data.total_tickets !== "number" ||
        !data.status_counts ||
        !data.priority_counts
      ) {
        throw new Error(
          "The server returned unexpected analytics data."
        );
      }

      setAnalytics(data);
    } catch (err) {
      errors.push(
        err.message || "Could not load ticket analytics."
      );
    }

    setError(errors.join(" "));
    setLoading(false);
  }

  useEffect(() => {
    loadTickets();
  }, []);

  // Use analytics from FastAPI when available.
  // Local counts provide a fallback if analytics cannot be loaded.
  const openCount =
    analytics?.status_counts?.open ??
    tickets.filter(
      (ticket) => normalizeStatus(ticket.status) === "open"
    ).length;

  const inProgressCount =
    analytics?.status_counts?.in_progress ??
    tickets.filter(
      (ticket) =>
        normalizeStatus(ticket.status) === "in_progress"
    ).length;

  const resolvedCount =
    analytics?.status_counts?.resolved ??
    tickets.filter(
      (ticket) =>
        ["resolved", "closed"].includes(
          normalizeStatus(ticket.status)
        )
    ).length;

  const totalCount = analytics?.total_tickets ?? tickets.length;

  const stats = [
    {
      label: "Total Tickets",
      value: totalCount,
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

  // Ticket counts grouped by category.
  // Missing categories safely default to zero.
  const categoryStats = [
    {
      label: "Account",
      value: analytics?.category_counts?.account ?? 0,
      icon: Users,
      className: "dashboard-blue",
    },
    {
      label: "Billing",
      value: analytics?.category_counts?.billing ?? 0,
      icon: CreditCard,
      className: "dashboard-green",
    },
    {
      label: "Technical",
      value: analytics?.category_counts?.technical ?? 0,
      icon: Wrench,
      className: "dashboard-purple",
    },
    {
      label: "General",
      value: analytics?.category_counts?.general ?? 0,
      icon: HelpCircle,
      className: "dashboard-orange",
    },
    {
      label: "Other",
      value: analytics?.category_counts?.other ?? 0,
      icon: Ticket,
      className: "dashboard-blue",
    },
  ];

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
            <strong>Dashboard notice</strong>
            <p>{error}</p>
          </div>
        </div>
      )}

      {/* Ticket summary cards */}
      <div className="dashboard-stats">
        {stats.map(({ label, value, icon: Icon, className }) => (
          <article className="dashboard-stat" key={label}>
            <div className={`dashboard-stat-icon ${className}`}>
              <Icon size={22} />
            </div>

            <div>
              <p>{label}</p>
              <h3>
                {loading && analytics === null && tickets.length === 0
                  ? "—"
                  : value}
              </h3>
            </div>
          </article>
        ))}
      </div>

      {/* Category analytics */}
      <section className="dashboard-section">
        <div className="dashboard-section-heading">
          <div>
            <h3>Tickets by Category</h3>
            <p>
              Distribution of support requests by category
            </p>
          </div>
        </div>

        <div className="dashboard-stats">
          {categoryStats.map(
            ({ label, value, icon: Icon, className }) => (
              <article className="dashboard-stat" key={label}>
                <div
                  className={`dashboard-stat-icon ${className}`}
                >
                  <Icon size={22} />
                </div>

                <div>
                  <p>{label}</p>
                  <h3>
                    {loading && analytics === null ? "—" : value}
                  </h3>
                </div>
              </article>
            )
          )}
        </div>
      </section>

      {/* Priority analytics */}
      <section className="dashboard-section">
        <div className="dashboard-section-heading">
          <div>
            <h3>Tickets by Priority</h3>
            <p>
              Distribution of support requests by priority
            </p>
          </div>
        </div>

        <div className="dashboard-stats">
          {[
            {
              label: "High Priority",
              value: analytics?.priority_counts?.high ?? 0,
              className: "dashboard-orange",
            },
            {
              label: "Medium Priority",
              value: analytics?.priority_counts?.medium ?? 0,
              className: "dashboard-purple",
            },
            {
              label: "Low Priority",
              value: analytics?.priority_counts?.low ?? 0,
              className: "dashboard-blue",
            },
          ].map(({ label, value, className }) => (
            <article className="dashboard-stat" key={label}>
              <div className={`dashboard-stat-icon ${className}`}>
                <AlertCircle size={22} />
              </div>

              <div>
                <p>{label}</p>
                <h3>
                  {loading && analytics === null ? "—" : value}
                </h3>
              </div>
            </article>
          ))}
        </div>
      </section>

      {/* Recent tickets */}
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
        ) : tickets.length === 0 ? (
          <div className="dashboard-empty">
            <Ticket size={30} />
            <strong>No tickets yet</strong>
            <p>
              Create a support ticket to see activity here.
            </p>
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

      {/* Quick actions */}
      <section className="dashboard-section">
        <div className="dashboard-section-heading">
          <div>
            <h3>Quick Actions</h3>
            <p>
              Continue working in your support workspace
            </p>
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
              <small>
                Create and update support requests
              </small>
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
              <small>
                Ask questions about uploaded documents
              </small>
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
              <small>
                Upload and manage support documents
              </small>
            </span>
            <ArrowRight size={18} />
          </button>
        </div>
      </section>
    </div>
  );
}
