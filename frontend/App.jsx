
import { useState } from "react";
import {
  MessageSquare, Ticket, Activity, UploadCloud
} from "lucide-react";
import "./index.css";

const pages = [
  { id: "chat", label: "AI Assistant", icon: MessageSquare },
  { id: "upload", label: "Knowledge Base", icon: UploadCloud },
  { id: "tickets", label: "Tickets", icon: Ticket },
  { id: "dashboard", label: "Overview", icon: Activity },
];

export default function App() {
  const [page, setPage] = useState("chat");

  return (
    <div className="layout">
      <aside className="sidebar">
        <h2>HelpDeskAI</h2>
        <p>Knowledge & support</p>

        {pages.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            className={page === id ? "active" : ""}
            onClick={() => setPage(id)}
          >
            <Icon size={18} /> {label}
          </button>
        ))}
      </aside>

      <main>
        <header>
          <h1>{pages.find(p => p.id === page)?.label}</h1>
          <p>Your AI-powered support workspace</p>
        </header>

        {page === "chat" && (
          <section className="panel">
            <h3>Ask your knowledge base</h3>
            <p>Ask questions about uploaded documents.</p>
            <textarea placeholder="Type your question..." />
            <button disabled>Ask question</button>
            <p className="muted">
              Chat will be connected on Day 7.
            </p>
          </section>
        )}

        {page === "upload" && (
          <section className="panel">
            <h3>Knowledge base</h3>
            <p>PDF and TXT document upload will be enabled on Day 4.</p>
          </section>
        )}

        {page === "tickets" && (
          <section className="panel">
            <h3>Support tickets</h3>
            <p>Ticket management will be enabled on Day 3.</p>
          </section>
        )}

        {page === "dashboard" && (
          <section className="panel">
            <h3>Support overview</h3>
            <p>Your analytics will appear here on Day 9.</p>
          </section>
        )}
      </main>
    </div>
  );
}
