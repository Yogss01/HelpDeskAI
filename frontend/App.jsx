import Tickets from "./components/Tickets.jsx";
import React from "react";
import { useState } from "react";
import Upload from "./components/Upload.jsx";
import {
  MessageSquare,
  Ticket,
  Activity,
  UploadCloud,
} from "lucide-react";
import "./index.css";
import Chat from "./components/Chat.jsx";

const pages = [
  { id: "chat", label: "AI Assistant", icon: MessageSquare },
  { id: "upload", label: "Knowledge Base", icon: UploadCloud },
  { id: "tickets", label: "Tickets", icon: Ticket },
  { id: "dashboard", label: "Overview", icon: Activity },
];

export default function App() {
  const [page, setPage] = useState("chat");

  const currentPage = pages.find((item) => item.id === page);

  return (
    <div className="layout">
      <aside className="sidebar">
        <h2>HelpDeskAI</h2>
        <p>Knowledge &amp; support</p>

        <nav aria-label="Main navigation">
          {pages.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              type="button"
              className={page === id ? "active" : ""}
              onClick={() => setPage(id)}
              aria-current={page === id ? "page" : undefined}
            >
              <Icon size={18} />
              <span>{label}</span>
            </button>
          ))}
        </nav>
      </aside>

      <main>
        <header>
          <h1>{currentPage?.label ?? "HelpDeskAI"}</h1>
          <p>Your AI-powered support workspace</p>
        </header>

        {page === "chat" && <Chat />}

        {page === "upload" && <Upload />}


        {page === "tickets" && <Tickets />}

        {page === "dashboard" && (
          <section className="panel">
            <h3>Support Overview</h3>
            <p>
              Monitor helpdesk activity and support requests.
            </p>
            <p className="muted">
              Dashboard statistics will be added after
              ticket management.
            </p>
          </section>
        )}
      </main>
    </div>
  );
}
