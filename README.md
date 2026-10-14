# HelpDeskAI

HelpDeskAI is a document-based support chatbot built with React, FastAPI, Ollama, and a retrieval system. It answers user questions using uploaded company documents and provides a fallback response when the required information is not available.

## Features

- Upload PDF and TXT documents.
- Extract and index document content for retrieval.
- Answer questions using Ollama (`llama3.2:3b`).
- Delete uploaded documents and their indexed information.
- Avoid duplicate document indexing.
- Create support tickets through the application.
- Return a fallback response when relevant information is unavailable.

## Technologies Used

- **Frontend:** React, JavaScript, Vite
- **Backend:** Python, FastAPI
- **LLM:** Ollama with `llama3.2:3b`
- **Retrieval:** Document processing and vector search
- **Version Control:** Git

## Prerequisites

Install the following before running the project:

- Python
- Node.js and npm
- Git
- Ollama

## Setup Instructions

### 1. Clone the repository

```bash
git clone YOUR_REPOSITORY_URL
cd helpdeskai
```

Replace `YOUR_REPOSITORY_URL` with your actual Git repository URL. If you already have the project locally, skip this step.

### 2. Start Ollama

Install Ollama and download the model:

```bash
ollama pull llama3.2:3b
```

Make sure Ollama is running before testing the chatbot.

### 3. Start the backend

Open a terminal in the project root:

```powershell
cd backend
python -m venv .venv
```

Activate the virtual environment in Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the project dependencies:

```powershell
pip install -r requirements.txt
```

Start the FastAPI server:

```powershell
uvicorn app.main:app --reload
```

If your FastAPI application uses a different module path, use the command configured for your project.

Backend API documentation is available at:

`http://127.0.0.1:8000/docs`

### 4. Start the frontend

Open a **second terminal** in VS Code:

```powershell
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite in your terminal.

## Usage

1. Start Ollama, the backend, and the frontend.
2. Open HelpDeskAI in your browser.
3. Upload a PDF or TXT document.
4. Ask a question about the uploaded content.
5. Verify that the chatbot answers using the document.
6. Delete the document and verify that its information is no longer retrieved.

## Fallback Response

When the answer cannot be found in the uploaded documents, HelpDeskAI responds:

> I couldn't find this information in the uploaded documents. Please create a support ticket for further assistance.

## Notes

- Keep secrets, passwords, virtual environments, and unnecessary generated files out of Git.
- Follow the project's dependency and configuration files when setting up a new environment.
