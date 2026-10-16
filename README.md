# HelpDeskAI

HelpDeskAI is a full-stack AI support assistant that answers questions using uploaded company documents. When the available documents do not contain an answer, the app can guide the user to create a support ticket. It combines a React interface, a FastAPI backend, retrieval-augmented generation (RAG), and a local language model powered by Ollama.

## Features

- **Document-based answers:** Ask questions about the uploaded knowledge base.
- **PDF and TXT uploads:** Add supported documents to the knowledge base through the UI.
- **Semantic retrieval:** Sentence Transformers creates embeddings, and FAISS finds relevant document chunks.
- **Answers with source citations:** Answers can identify the document used as evidence.
- **Safe fallback for missing information:** When relevant evidence is not found, the assistant says it could not find the answer and offers the support-ticket flow.
- **Support ticket management:** Create tickets and view or update their status.
- **Persistent ticket storage:** SQLite stores ticket data so status changes remain after a backend restart.
- **Local LLM:** Ollama runs the configured `llama3.2:3b` model locally, avoiding a dependency on paid hosted LLM API credits for answer generation.
- **API and retrieval testing:** Includes a seven-scenario API test script and a retrieval evaluation script.

## Tech stack

| Area | Technology |
|---|---|
| Frontend | React, Vite, JavaScript, CSS |
| Backend | Python, FastAPI, Uvicorn |
| Database | SQLite |
| Embeddings | Sentence Transformers, `all-MiniLM-L6-v2` |
| Vector search | FAISS |
| Language model | Ollama, `llama3.2:3b` |
| Document processing | PDF and TXT ingestion; PDF extraction/OCR support where configured |
| Icons | Lucide React |

## How it works

1. A user uploads a PDF or TXT file in the React interface.
2. The backend extracts the document text and splits it into smaller chunks.
3. Sentence Transformers converts those chunks into embeddings, which are stored in a FAISS index.
4. When the user asks a question, the backend searches the index for relevant chunks.
5. The retrieved evidence is passed to the local Ollama model to generate an answer.
6. The app returns the answer and source information when available. If the documents do not provide enough evidence, it returns a fallback response and can offer ticket creation.
7. Ticket details and status are stored in SQLite.

## Project structure

```text
HelpDeskAI/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application and API routes
│   │   ├── rag.py               # Chunking, embeddings, and FAISS retrieval
│   │   ├── document_store.py    # Document ingestion and storage helpers
│   │   ├── llm.py               # Ollama answer generation
│   │   ├── database.py          # SQLite connection and initialization
│   │   ├── schemas.py            # API request/response and ticket schemas
│   │   └── classifier.py        # Classification helpers
│   ├── requirements.txt
│   ├── test_rag_api.py          # API behavior tests
│   ├── evaluate_rag.py          # Retrieval evaluation
│   └── data/                    # Generated/local data; do not commit private uploads
├── frontend/
│   ├── components/
│   │   ├── Chat.jsx
│   │   ├── Upload.jsx
│   │   └── Tickets.jsx
│   ├── App.jsx
│   ├── main.jsx
│   ├── index.html
│   └── index.css
├── sample_docs/                 # Sample documents, if included in your checkout
├── .gitignore
└── README.md
```

Some local/generated folders or optional files may not exist until you run the application.

## Prerequisites

Install these before running the project:

- **Python 3.12** (the project has been developed and tested in a Python 3.12 virtual environment)
- **Node.js and npm**
- **Ollama** for running the local language model
- **Git** (optional, if cloning the repository)

## Setup on Windows

The commands below use PowerShell and match the project's current Windows workflow.

### 1. Get the project

If you have not cloned the repository yet:

```powershell
git clone https://github.com/Yogss01/HelpDeskAI.git
cd HelpDeskAI
```

If the project is already on your computer, open its folder in VS Code and use the existing project directory instead.

### 2. Set up the Python backend

From the project root:

```powershell
cd backend
py -3.12 -m venv .venv
```

Activate the environment:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
```

Install the backend dependencies:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell activation is unavailable, you can use the virtual environment's Python executable directly, for example:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 3. Set up Ollama and download the model

Install Ollama from [ollama.com](https://ollama.com/), then open a terminal and run:

```powershell
ollama pull llama3.2:3b
```

Confirm the model is available:

```powershell
ollama list
```

Make sure Ollama is running before testing chat responses. The backend is configured to use `llama3.2:3b`.

### 4. Start the backend

From the `backend` directory, with the virtual environment activated:

```powershell
python -m uvicorn app.main:app --reload
```

The backend should be available at `http://127.0.0.1:8000`.

Useful backend URLs:

- API health check: <http://127.0.0.1:8000/api/health>
- Interactive API documentation: <http://127.0.0.1:8000/docs>

Keep this terminal open while using the application.

### 5. Set up and start the frontend

Open a **second terminal** in VS Code. From the project root, run:

```powershell
cd frontend
npm install
npm.cmd run dev
```

Open the local URL printed by Vite, normally <http://localhost:5173/>.

> On Windows PowerShell, use `npm.cmd` if script execution policy prevents the `npm` command from running.

## Using the application

1. Open the frontend in your browser.
2. Go to the Knowledge Base page and upload a PDF or TXT document.
3. Open AI Assistant and ask a question that the uploaded document answers.
4. Check the answer and the source citation.
5. Ask a question that is not covered by the knowledge base and use the offered ticket flow to create a support ticket.
6. Open Tickets to review tickets and update their status.

For useful results, upload relevant documents before asking questions. The assistant is designed to use retrieved document evidence rather than answer every general-knowledge question.

## API endpoints

The application includes these main API routes:

| Endpoint | Purpose |
|---|---|
| `GET /api/health` | Check that the backend is responding |
| `POST /api/chat` | Ask a question and receive an answer/ticket guidance |
| `POST /api/documents` | Upload a document |
| `GET /api/tickets` | Retrieve tickets |
| `/api/analytics` | Access application analytics |

See <http://127.0.0.1:8000/docs> for the live route list, HTTP methods, request schemas, and response details. The exact methods supported by individual ticket or document operations are defined in the running API documentation.

## Run the API tests

Start the backend first and keep it running. Then open a separate terminal at the **project root** and run:

```powershell
python backend/test_rag_api.py
```

The script checks seven scenarios, including questions answered by documents, questions with no supporting evidence, password-reset guidance, dress-code information, and retrieval of a test code. A successful run prints a summary such as `Passed: 7/7`. Results depend on the current uploaded documents and application state.

## Evaluate retrieval

The repository also includes `backend/evaluate_rag.py` for evaluating retrieval behavior. Run it according to the imports and working-directory assumptions in the script; if running from the backend directory, use:

```powershell
cd backend
python evaluate_rag.py
```

## Troubleshooting

- **`localhost:5173` does not open:** Check that `npm.cmd run dev` is running in the frontend terminal.
- **The API is unavailable:** Check that the backend terminal is running without errors and visit <http://127.0.0.1:8000/api/health>.
- **Ollama/model errors:** Confirm Ollama is installed, running, and lists `llama3.2:3b` with `ollama list`.
- **The assistant cannot answer from a document:** Confirm the upload succeeded, the document appears in the Knowledge Base, and the question is answered by its content. Re-upload a changed file if necessary.
- **A question leads to ticket creation:** This is expected when the retriever does not find enough supporting document evidence.
- **PowerShell blocks npm scripts:** Use `npm.cmd` instead of `npm`.
- **Python virtual environment activation is blocked:** Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned` in that terminal, then activate `.venv` again.

## Git and data hygiene

- Do not commit `.venv/`, `node_modules/`, build output, local database files, generated FAISS indexes, private uploaded documents, or `.env` secrets.
- Keep any machine-specific paths and credentials out of the repository.
- Review `git status` before committing changes, and use `git diff --check` to check for whitespace errors.

## Current validation

During development, the seven-case API test script completed with **7/7 tests passing**, the health endpoint returned `{"status":"ok"}`, and the user confirmed that the frontend upload, chat, citation, ticket creation, and ticket status workflows worked manually. Re-run the commands above after making changes to validate your current checkout.

## Future improvements

- Add automated frontend tests and broader backend test coverage.
- Add document-level metadata and more detailed citation snippets.
- Add configurable retrieval thresholds and a larger evaluation dataset.
- Improve authentication, authorization, logging, and deployment configuration before exposing the app beyond a trusted local environment.

## License

No license is specified here. Add a `LICENSE` file before distributing the project under a particular open-source license.
