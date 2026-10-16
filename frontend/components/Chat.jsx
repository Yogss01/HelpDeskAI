import React, { useState } from "react";
import {
  Send,
  Bot,
  User,
  Ticket,
  LoaderCircle,
  FileText,
  X,
} from "lucide-react";

const API_URL = "http://127.0.0.1:8000";

export default function Chat() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Support ticket form state.
  const [ticketForm, setTicketForm] = useState(null);
  const [ticketTitle, setTicketTitle] = useState("");
  const [ticketDescription, setTicketDescription] = useState("");
  const [ticketCategory, setTicketCategory] = useState("technical");
  const [ticketPriority, setTicketPriority] = useState("medium");
  const [ticketSubmitting, setTicketSubmitting] = useState(false);

  // Send a question to HelpDeskAI.
  async function sendMessage(event) {
    event.preventDefault();

    const text = question.trim();

    if (!text || loading) return;

    setMessages((previous) => [
      ...previous,
      { role: "user", content: text },
    ]);

    setQuestion("");
    setError("");
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/api/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question: text }),
      });

      if (!response.ok) {
        throw new Error(`Server returned HTTP ${response.status}`);
      }

      const data = await response.json();

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content: data.answer,
          sources: Array.isArray(data.sources) ? data.sources : [],
          needsTicket: data.needs_ticket ?? false,
          ticketCreated: false,
          originalQuestion: text,
        },
      ]);
    } catch (err) {
      setError(
        err.message ||
        "Could not connect to HelpDeskAI. Check that FastAPI is running and CORS is configured."
      );
    } finally {
      setLoading(false);
    }
  }

  // Open the ticket form.
  function openTicketForm(messageIndex) {
    const message = messages[messageIndex];

    if (!message || message.ticketCreated || ticketSubmitting) {
      return;
    }

    setError("");
    setTicketTitle(
      `Help needed: ${message.originalQuestion}`.slice(0, 200)
    );
    setTicketDescription(
      `Question asked in HelpDeskAI:\n${message.originalQuestion}\n\n` +
      `AI response:\n${message.content}`
    );
    setTicketCategory("technical");
    setTicketPriority("medium");
    setTicketForm({ messageIndex });
  }

  // Close the ticket form.
  function closeTicketForm() {
    if (ticketSubmitting) return;

    setTicketForm(null);
    setTicketTitle("");
    setTicketDescription("");
    setError("");
  }

  // Submit a support ticket.
  async function submitTicket(event) {
    event.preventDefault();

    if (
      !ticketForm ||
      !ticketTitle.trim() ||
      !ticketDescription.trim() ||
      ticketSubmitting
    ) {
      return;
    }

    const messageIndex = ticketForm.messageIndex;

    setError("");
    setTicketSubmitting(true);

    try {
      const response = await fetch(`${API_URL}/api/tickets`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          title: ticketTitle.trim(),
          description: ticketDescription.trim(),
          category: ticketCategory,
          priority: ticketPriority,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail
            ? JSON.stringify(data.detail)
            : "Could not create the support ticket."
        );
      }

      setMessages((previous) =>
        previous.map((item, index) =>
          index === messageIndex
            ? {
              ...item,
              ticketCreated: true,
              createdTicketId: data.id,
            }
            : item
        )
      );

      setTicketForm(null);
      setTicketTitle("");
      setTicketDescription("");
    } catch (err) {
      setError(err.message || "Could not create the support ticket.");
    } finally {
      setTicketSubmitting(false);
    }
  }

  return (
    <section className="panel chat-panel">
      {/* Chat header */}
      <div className="chat-header">
        <div className="chat-header-icon">
          <Bot size={23} />
        </div>

        <div className="chat-header-text">
          <h3>AI Assistant</h3>
          <p>
            <span className="chat-status-dot" />
            Your intelligent support companion
          </p>
        </div>
      </div>

      {/* Messages */}
      <div className="chat-messages" aria-live="polite">
        {messages.length === 0 && (
          <div className="chat-welcome">
            <div className="chat-welcome-icon">
              <Bot size={30} />
            </div>

            <h3>How can I help you today?</h3>

            <p>
              Ask me about company policies, IT support,
              password resets, or your knowledge base.
            </p>

          </div>
        )}

        {messages.map((message, index) => {
          const isUser = message.role === "user";

          return (
            <article
              className={`chat-message ${isUser ? "user-message" : "assistant-message"
                }`}
              key={index}
            >
              <div className="message-heading">
                <span className="message-avatar">
                  {isUser ? (
                    <User size={16} />
                  ) : (
                    <Bot size={16} />
                  )}
                </span>

                <strong>
                  {isUser ? "You" : "HelpDeskAI"}
                </strong>

                {!isUser && (
                  <span className="ai-label">AI</span>
                )}
              </div>

              <div className="message-content">
                <p>{message.content}</p>
              </div>

              {/* Sources used by the AI */}
              {!isUser && message.sources.length > 0 && (
                <div className="sources">
                  <strong className="sources-heading">
                    <FileText size={15} />
                    Sources used
                  </strong>

                  {message.sources.map((source, sourceIndex) => (
                    <div
                      className="source-item"
                      key={sourceIndex}
                    >
                      <div className="source-title">
                        <FileText size={16} />

                        <strong>
                          {source.filename ??
                            source.source ??
                            "Company document"}
                        </strong>
                      </div>

                      {source.excerpt?.trim() ? (
                        <p className="source-excerpt">
                          {source.excerpt.trim()}
                        </p>
                      ) : (
                        <p className="source-excerpt">
                          No excerpt available for this source.
                        </p>
                      )}

                      {typeof source.score === "number" && (
                        <small className="source-score">
                          Retrieval score:{" "}
                          {source.score.toFixed(3)}
                        </small>
                      )}
                    </div>
                  ))}
                </div>
              )}

              {/* Ticket assistance */}
              {!isUser && message.needsTicket && (
                <div className="ticket-notice">
                  <p>
                    <Ticket size={17} />
                    This question needs further assistance.
                  </p>

                  {message.ticketCreated ? (
                    <p role="status">
                      Support ticket created successfully!
                      <br />
                      Ticket ID: {message.createdTicketId}
                    </p>
                  ) : (
                    <button
                      type="button"
                      onClick={() => openTicketForm(index)}
                      disabled={ticketSubmitting}
                    >
                      <Ticket size={16} />
                      Create Support Ticket
                    </button>
                  )}
                </div>
              )}
            </article>
          );
        })}

        {/* AI loading indicator */}
        {loading && (
          <div className="chat-message assistant-message typing-message">
            <div className="message-heading">
              <span className="message-avatar">
                <Bot size={16} />
              </span>

              <strong>HelpDeskAI</strong>
            </div>

            <div className="typing-indicator">
              <span />
              <span />
              <span />
              <small>Thinking...</small>
            </div>
          </div>
        )}
      </div>

      {/* Error message */}
      {error && (
        <p className="error-message" role="alert">
          {error}
        </p>
      )}

      {/* Editable ticket form */}
      {ticketForm && (
        <section className="ticket-form-panel">
          <div className="ticket-form-heading">
            <div>
              <h3>Create Support Ticket</h3>
              <p className="muted">
                Review the details before submitting.
              </p>
            </div>

            <button
              type="button"
              className="ticket-close-button"
              onClick={closeTicketForm}
              disabled={ticketSubmitting}
              aria-label="Close ticket form"
              title="Close"
            >
              <X size={18} />
            </button>
          </div>

          <form onSubmit={submitTicket} className="ticket-form">
            <div>
              <label htmlFor="ticket-title">Title</label>
              <input
                id="ticket-title"
                type="text"
                value={ticketTitle}
                onChange={(event) =>
                  setTicketTitle(event.target.value)
                }
                maxLength={200}
                required
                placeholder="Enter ticket title"
                disabled={ticketSubmitting}
              />
            </div>

            <div>
              <label htmlFor="ticket-description">
                Description
              </label>
              <textarea
                id="ticket-description"
                value={ticketDescription}
                onChange={(event) =>
                  setTicketDescription(event.target.value)
                }
                rows={6}
                required
                placeholder="Describe your issue"
                disabled={ticketSubmitting}
              />
            </div>

            <div>
              <label htmlFor="ticket-category">Category</label>
              <select
                id="ticket-category"
                value={ticketCategory}
                onChange={(event) =>
                  setTicketCategory(event.target.value)
                }
                disabled={ticketSubmitting}
              >
                <option value="technical">Technical</option>
                <option value="account">Account</option>
                <option value="software">Software</option>
                <option value="hardware">Hardware</option>
                <option value="other">Other</option>
              </select>
            </div>

            <div>
              <label htmlFor="ticket-priority">Priority</label>
              <select
                id="ticket-priority"
                value={ticketPriority}
                onChange={(event) =>
                  setTicketPriority(event.target.value)
                }
                disabled={ticketSubmitting}
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </div>

            <div className="ticket-form-actions">
              <button
                type="button"
                onClick={closeTicketForm}
                disabled={ticketSubmitting}
              >
                Cancel
              </button>

              <button
                type="submit"
                disabled={
                  ticketSubmitting ||
                  !ticketTitle.trim() ||
                  !ticketDescription.trim()
                }
              >
                {ticketSubmitting ? (
                  <>
                    <LoaderCircle
                      size={16}
                      className="spinner"
                    />
                    Submitting...
                  </>
                ) : (
                  <>
                    <Ticket size={16} />
                    Submit Ticket
                  </>
                )}
              </button>
            </div>
          </form>
        </section>
      )}

      {/* Message input */}
      <form className="chat-form chat-form-raised" onSubmit={sendMessage}>
        <textarea
          aria-label="Your question"
          placeholder="Message HelpDeskAI..."
          value={question}
          onChange={(event) =>
            setQuestion(event.target.value)
          }
          disabled={loading}
          maxLength={2000}
          rows={2}
        />

        <button
          type="submit"
          disabled={loading || !question.trim()}
          aria-label="Send message"
        >
          {loading ? (
            <LoaderCircle size={18} className="spinner" />
          ) : (
            <Send size={18} />
          )}
          <span>{loading ? "Sending..." : "Send"}</span>
        </button>
      </form>

      <p className="chat-footer-note">
        HelpDeskAI can make mistakes. Verify important information
        with your support team.
      </p>
    </section>
  );
}
