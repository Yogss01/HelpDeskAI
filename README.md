# HelpDeskAI — AI-Powered IT Support Assistant

HelpDeskAI is an AI-powered IT support application that helps users find answers from internal support documents, manage knowledge-base files, and create and track support tickets through a simple web interface.

## Features

- **AI Assistant:** Ask questions about uploaded support documents and receive context-based answers.
- **Knowledge Base:** Upload and manage documents used by the AI assistant.
- **Document Retrieval:** Find relevant information from stored documents to help answer user questions.
- **Ticket Management:** Create support tickets with titles, descriptions, categories, and priorities.
- **Ticket Status Tracking:** Update and monitor ticket statuses, including Open, In Progress, and Resolved.
- **Overview Dashboard:** View ticket statistics and recent support requests.
- **Local LLM:** Run AI responses locally using Ollama and the `llama3.2:3b` model.
- **REST API:** Use FastAPI endpoints to connect the frontend and backend.

## Technology Stack

| Component | Technology |
|---|---|
| Frontend | React, JavaScript, CSS |
| Backend | Python, FastAPI |
| AI Model Runtime | Ollama |
| Language Model | `llama3.2:3b` |
| API Communication | HTTP and REST |
| Ticket Storage | SQLite, if configured in the backend |
| Document Retrieval | Project-configured document indexing and retrieval components |

## Project Structure

```text
helpdeskai/
├── backend/
│   ├── app/
│   │   ├── database.py
│   │   ├── document_store.py
│   │   ├── llm.py
│   │   ├── main.py
│   │   ├── rag.py
│   │   └── schemas.py
│   └── requirements.txt
├── frontend/
│   ├── components/
│   │   ├── Chat.jsx
│   │   ├── Dashboard.jsx
│   │   ├── Tickets.jsx
│   │   └── Upload.jsx
│   ├── App.jsx
│   ├── index.css
│   └── package.json
├── .gitignore
└── README.md
```

*Note: The structure above shows the main application files. Your local project may contain additional files.*

## Prerequisites

Install the following before running the application:

- Python 3.10 or a compatible version supported by your dependencies
- Node.js and npm
- Git
- Ollama

## Installation and Setup

### 1. Clone the repository

```powershell
git clone https://github.com/Yogss01/HelpDeskAI.git
cd HelpDeskAI
```

### 2. Set up Ollama

Install Ollama from [https://ollama.com](https://ollama.com).

Download the model used by the application:

```powershell
ollama pull llama3.2:3b
```

Make sure Ollama is running before testing AI responses.

### 3. Set up the Python backend

From the project root, run:

```powershell
cd backend
python -m venv .venv
```

Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the backend dependencies:

```powershell
pip install -r requirements.txt
```

Start the FastAPI server:

```powershell
uvicorn app.main:app --reload
```

The backend should be available at:

- API base URL: `http://127.0.0.1:8000`
- Interactive API documentation: `http://127.0.0.1:8000/docs`

Keep this terminal open while using the application.

### 4. Set up the React frontend

Open a second PowerShell terminal in VS Code. From the project root, run:

```powershell
cd frontend
npm install
npm run dev
```

Open the local URL displayed by Vite, commonly:

`http://localhost:5173`

Keep the frontend terminal running as well.

## How to Use HelpDeskAI

1. Start the backend, frontend, and Ollama.
2. Open the application in your browser.
3. Navigate to **Knowledge Base** and upload support documents.
4. Open **AI Assistant** and ask questions related to the uploaded documents.
5. Use **Tickets** to create support requests and update their statuses.
6. Open **Overview** to view ticket counts and recent support activity.

## API Endpoints

The application includes ticket endpoints such as:

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/tickets` | Retrieve tickets |
| POST | `/api/tickets` | Create a ticket |
| PATCH | `/api/tickets/{ticketId}` | Update ticket information |

Additional document and AI endpoints are available through the FastAPI documentation at `/docs`.

## Project Goals

HelpDeskAI demonstrates how a web application can combine a React interface, a Python REST API, local language models, document-based question answering, and ticket management into one support workspace.

## Future Improvements

- Authentication and role-based access control
- Improved document-processing and retrieval accuracy
- Ticket search, filtering, and analytics
- Automated testing and error monitoring
- Production deployment and secure configuration

## Author

**Yogss01**

GitHub repository: [https://github.com/Yogss01/HelpDeskAI](https://github.com/Yogss01/HelpDeskAI)
