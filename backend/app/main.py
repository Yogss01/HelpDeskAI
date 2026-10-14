from time import perf_counter
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from app.database import connect, initialise
from app.schemas import TicketCreate, TicketUpdate
from app.document_store import extract_document
from app.rag import (
    add_document,
    search_documents,
    delete_document as remove_document_from_index,
)
from pathlib import Path
import json
from app.llm import generate_answer

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialise()
    yield


app = FastAPI(title="HelpDeskAI", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    question: str = Field(min_length=2, max_length=2000)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/tickets")
def list_tickets():
    with connect() as db:
        rows = db.execute(
            "SELECT * FROM tickets ORDER BY created_at DESC"
        ).fetchall()
        return [dict(row) for row in rows]


@app.post("/api/tickets", status_code=201)
def create_ticket(ticket: TicketCreate):
    item = {
        "id": str(uuid4()),
        **ticket.model_dump(),
        "status": "open",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    with connect() as db:
        db.execute(
            """
            INSERT INTO tickets
            (id, title, description, category, priority,
             status, created_at)
            VALUES
            (:id, :title, :description, :category, :priority,
             :status, :created_at)
            """,
            item,
        )

    return item


@app.patch("/api/tickets/{ticket_id}")
def update_ticket(ticket_id: str, update: TicketUpdate):
    with connect() as db:
        result = db.execute(
            "UPDATE tickets SET status = ? WHERE id = ?",
            (update.status, ticket_id),
        )

        if result.rowcount == 0:
            raise HTTPException(404, "Ticket not found")

        row = db.execute(
            "SELECT * FROM tickets WHERE id = ?",
            (ticket_id,),
        ).fetchone()

    return dict(row)


@app.post("/api/documents")
async def upload_document(file: UploadFile = File(...)):
    filename = file.filename or ""
    content = await file.read()

    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(413, "Maximum upload size is 10 MB")

    try:
        text = extract_document(filename, content)
        print("EXTRACTED DOCUMENT TEXT:", text[:3000])
        chunks = add_document(text, filename)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    finally:
        await file.close()

    return {
        "filename": filename,
        "chunks_indexed": chunks,
        "status": "indexed",
    }


@app.get("/api/documents")
def list_documents():
    """List documents stored in the knowledge base."""

    chunks_file = Path("data") / "chunks.json"

    if not chunks_file.exists():
        return []

    records = json.loads(
        chunks_file.read_text(encoding="utf-8")
    )

    documents = {}

    for record in records:
        filename = record.get("source", "Unknown document")

        if filename not in documents:
            documents[filename] = {
                "filename": filename,
                "chunks": 0,
                "status": "indexed",
            }

        documents[filename]["chunks"] += 1

    return list(documents.values())

@app.delete("/api/documents")
def delete_document_endpoint(filename: str):
    """Delete a document from the knowledge base."""

    removed_count = remove_document_from_index(filename)

    if removed_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Document not found in the knowledge base.",
        )

    return {
        "filename": filename,
        "chunks_removed": removed_count,
        "status": "deleted",
    }


@app.post("/api/chat")
def chat(request: ChatRequest):
    
    question = request.question.strip()
    question_lower = question.lower()

    fallback_answer = (
        "I couldn't find this information in the uploaded documents. "
        "Please create a support ticket for further assistance."
    )

    # Handle questions asking what to do when information is missing.
    missing_answer_phrases = [
        "if the document does not contain the answer",
        "if the document doesn't contain the answer",
        "if the answer is not in the document",
        "if the answer isn't in the document",
        "if the information is not in the document",
    ]

    if any(
        phrase in question_lower
        for phrase in missing_answer_phrases
    ):
        return {
            "answer": fallback_answer,
            "sources": [],
            "needs_ticket": True,
        }


    search_start = perf_counter()

    # Use a focused search phrase for dress-code questions.
    is_dress_question = any(
        term in question_lower
        for term in [
            "dress code",
            "dress",
            "attire",
            "clothing",
            "what to wear",
            "appearance",
        ]
    )

    if is_dress_question:
        search_query = "dress and appearance"
    else:
        search_query = question

    results = search_documents(search_query, top_k=20)

    # DEBUG: Check the retrieved document chunks.
    print(f"SEARCH QUERY: {search_query}")
    print(f"RETRIEVED CHUNKS: {len(results)}")

    for item in results[:5]:
        print("SCORE:", round(float(item.get("score", 0)), 3))
        print("SOURCE:", item.get("source", "Unknown"))
        print("TEXT:", item.get("text", "")[:300])
        print("-" * 40)

    search_time = perf_counter() - search_start
    print(f"DOCUMENT SEARCH TIME: {search_time:.2f} seconds")
    

    # DEBUG: Print retrieved document chunks.
    print(f"RETRIEVED CHUNKS: {len(results)}")

    for item in results[:5]:
        print("SCORE:", round(float(item.get("score", 0)), 3))
        print("SOURCE:", item.get("source", "Unknown"))
        print("TEXT:", item.get("text", "")[:300])
        print("-" * 40)

    search_time = perf_counter() - search_start
    print(f"DOCUMENT SEARCH TIME: {search_time:.2f} seconds")


    # Remove duplicate chunks.
    unique_results = []
    seen = set()

    for item in results:
        text = item.get("text", "").strip()
        filename = item.get("source", "Unknown source")
        key = (filename, text)

        if text and key not in seen:
            seen.add(key)
            unique_results.append(item)

    # Prioritize the relevant policy section for dress-code questions.
    if any(term in question_lower for term in [
        "dress code",
        "dress",
        "attire",
        "clothing",
        "what to wear",
        "appearance",
    ]):
        matching = [
            item
            for item in unique_results
            if (
                "neat, clean and appropriate" in item["text"].lower()
                or "dress and appearance" in item["text"].lower()
                or (
                    "appearance" in item["text"].lower()
                    and "personal hygiene" in item["text"].lower()
                )
            )
        ]

        sources = matching[:2] if matching else unique_results[:4]
    # Prioritize direct evidence for employee-name questions.
    elif "employee name" in question_lower:
        matching = [
            item for item in unique_results
            if "employee name" in item["text"].lower()
        ]

        sources = matching[:1] if matching else unique_results[:4]

    else:
        sources = unique_results[:4]


    llm_start = perf_counter()
    answer = generate_answer(question, sources)
    llm_time = perf_counter() - llm_start
    print(f"OLLAMA GENERATION TIME: {llm_time:.2f} seconds")

    if not answer or not isinstance(answer, str):
        answer = (
            "I couldn't find this information in the uploaded documents. "
            "Please create a support ticket for further assistance."
        )

    fallback_text = (
        "I couldn't find this information in the uploaded documents. "
        "Please create a support ticket for further assistance."
    )

    needs_ticket = (
        answer.strip() == fallback_text
        or answer.strip().startswith("Fallback answer:")
    )

    if needs_ticket:
        sources = []

    return {
        "answer": answer,
        "sources": [
            {
                "filename": item.get("source", "Unknown source"),
                "excerpt": item.get("text", "")[:250],
                "score": round(float(item.get("score", 0)), 3),
            }
            for item in sources
        ],
        "needs_ticket": needs_ticket,
    }
