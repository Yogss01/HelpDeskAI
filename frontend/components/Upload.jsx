
import React, { useEffect, useState } from "react";
import {
  UploadCloud,
  FileText,
  CheckCircle,
  AlertCircle,
} from "lucide-react";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
export default function Upload() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState(false);

  const [documents, setDocuments] = useState([]);
  const [loadingDocuments, setLoadingDocuments] = useState(true);
  const [listError, setListError] = useState("");
  const [deletingFilename, setDeletingFilename] = useState("");

  // Load the documents from the backend.
  async function loadDocuments() {
    setLoadingDocuments(true);
    setListError("");

    try {
      const response = await fetch(`${API_URL}/api/documents`);

      if (!response.ok) {
        throw new Error("Could not load uploaded documents.");
      }

      const data = await response.json();
      setDocuments(data);
    } catch (err) {
      setListError(
        err.message || "Could not connect to the backend."
      );
    } finally {
      setLoadingDocuments(false);
    }
  }

  // Load documents when the component first appears.
  useEffect(() => {
    loadDocuments();
  }, []);

  // Upload a PDF or TXT document.
  async function handleUpload(event) {
    event.preventDefault();

    // Save the form reference before the async operation.
    const form = event.currentTarget;

    if (!file || loading) return;

    setLoading(true);
    setMessage("");
    setError(false);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(`${API_URL}/api/documents`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(
          data.detail || `Upload failed (${response.status})`
        );
      }

      if (data.chunks_indexed === 0) {
        setMessage(
          `${file.name} is already indexed. No duplicate chunks were added.`
        );
      } else {
        setMessage(
          `${file.name} uploaded successfully. ` +
          `${data.chunks_indexed} chunks indexed.`
        );
      }

      // Clear the file selection and reset the form.
      form.reset();
      setFile(null);

      // Refresh the document list after uploading.
      await loadDocuments();
    } catch (err) {
      setError(true);
      setMessage(
        err.message ||
        "Could not upload the file. Check that the backend is running."
      );
    } finally {
      setLoading(false);
    }
  }

  // Delete a document from the knowledge base.
  async function handleDelete(document) {
    const confirmed = window.confirm(
      `Are you sure you want to delete "${document.filename}"?`
    );

    if (!confirmed) return;

    setDeletingFilename(document.filename);
    setMessage("");
    setError(false);

    try {
      const response = await fetch(
        `${API_URL}/api/documents?filename=${encodeURIComponent(
          document.filename
        )}`,
        {
          method: "DELETE",
        }
      );

      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(
          data.detail || "Could not delete the document."
        );
      }

      setMessage(
        `${document.filename} deleted successfully. ` +
        `${data.chunks_removed} chunks removed.`
      );

      // Refresh the list after deleting.
      await loadDocuments();
    } catch (err) {
      setError(true);
      setMessage(
        err.message || "Could not delete the document."
      );
    } finally {
      setDeletingFilename("");
    }
  }

  return (
    <section className="panel">
      <h3>Upload company documents</h3>

      <p>
        Add company FAQs, IT policies, and support guides to your
        knowledge base. HelpDeskAI can use these documents to answer questions.
      </p>

      {/* Document upload form */}
      <form onSubmit={handleUpload}>
        <label htmlFor="document-file">
          Choose a PDF or TXT file
        </label>

        <input
          id="document-file"
          type="file"
          accept=".pdf,.txt,application/pdf,text/plain"
          onChange={(event) => {
            setFile(event.target.files?.[0] ?? null);
            setMessage("");
            setError(false);
          }}
          disabled={loading}
          required
        />

        {file && (
          <p>
            <FileText size={18} /> Selected: {file.name}
          </p>
        )}

        <button type="submit" disabled={!file || loading}>
          <UploadCloud size={18} />
          {loading ? "Uploading..." : "Upload document"}
        </button>
      </form>

      {/* Upload or delete success/error message */}
      {message && (
        <p
          role={error ? "alert" : "status"}
          className={
            error ? "error-message" : "success-message"
          }
        >
          {error ? (
            <AlertCircle size={18} />
          ) : (
            <CheckCircle size={18} />
          )}
          {" "}{message}
        </p>
      )}

      <hr />

      {/* Uploaded documents list */}
      <h3>Uploaded Documents</h3>

      {loadingDocuments && <p>Loading documents...</p>}

      {listError && (
        <p role="alert" className="error-message">
          <AlertCircle size={18} /> {listError}{" "}
          <button type="button" onClick={loadDocuments}>
            Retry
          </button>
        </p>
      )}

      {!loadingDocuments &&
        !listError &&
        documents.length === 0 && (
          <p>No documents have been indexed yet.</p>
        )}

      {!loadingDocuments &&
        !listError &&
        documents.length > 0 && (
          <ul>
            {documents.map((document) => (
              <li key={document.filename}>
                <FileText size={18} />

                <strong>{document.filename}</strong>

                <p>
                  {document.chunks} stored chunks · {document.status}
                </p>

                <button
                  type="button"
                  onClick={() => handleDelete(document)}
                  disabled={
                    deletingFilename === document.filename
                  }
                >
                  {deletingFilename === document.filename
                    ? "Deleting..."
                    : "Delete"}
                </button>
              </li>
            ))}
          </ul>
        )}
    </section>
  );
}
