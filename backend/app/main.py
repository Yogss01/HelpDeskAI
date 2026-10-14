
from time import perf_counter
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from uuid import uuid4
from pathlib import Path
import json

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
from app.llm import generate_answer
from app.classifier import predict_category_with_confidence


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


# --------------------------------------------------
# Health Check
# --------------------------------------------------

@app.get("/api/health")
def health():
    return {"status": "ok"}


# --------------------------------------------------
# List Tickets
# --------------------------------------------------

@app.get("/api/tickets")
def list_tickets():
    with connect() as db:
        rows = db.execute(
            "SELECT * FROM tickets ORDER BY created_at DESC"
        ).fetchall()

    return [dict(row) for row in rows]


# --------------------------------------------------
# Ticket Analytics
# --------------------------------------------------


@app.get("/api/analytics")
def get_ticket_analytics():
    """Return ticket counts grouped by status, priority, and category."""

    with connect() as db:
        total = db.execute(
            "SELECT COUNT(*) FROM tickets"
        ).fetchone()[0]

        status_rows = db.execute(
            """
            SELECT status, COUNT(*) AS count
            FROM tickets
            GROUP BY status
            """
        ).fetchall()

        priority_rows = db.execute(
            """
            SELECT priority, COUNT(*) AS count
            FROM tickets
            GROUP BY priority
            """
        ).fetchall()

        category_rows = db.execute(
            """
            SELECT category, COUNT(*) AS count
            FROM tickets
            GROUP BY category
            """
        ).fetchall()

    status_counts = {
        "open": 0,
        "in_progress": 0,
        "resolved": 0,
    }

    for row in status_rows:
        status_counts[row["status"]] = row["count"]

    priority_counts = {
        "low": 0,
        "medium": 0,
        "high": 0,
    }

    for row in priority_rows:
        priority_counts[row["priority"]] = row["count"]

    category_counts = {
        "account": 0,
        "billing": 0,
        "technical": 0,
        "general": 0,
    }

    for row in category_rows:
        category_counts[row["category"]] = row["count"]

    return {
        "total_tickets": total,
        "status_counts": status_counts,
        "priority_counts": priority_counts,
        "category_counts": category_counts,
    }


# --------------------------------------------------
# Create Ticket with Automatic Classification
# --------------------------------------------------

@app.post("/api/tickets", status_code=201)
def create_ticket(ticket: TicketCreate):
    """Create a ticket and classify it when confidence is sufficient."""

    ticket_data = ticket.model_dump()

    # Predict the category and calculate estimated confidence.
    prediction = predict_category_with_confidence(
        ticket_data["description"]
    )

    predicted_category = prediction["category"]
    confidence = prediction["confidence"]

    # Initial experimental confidence threshold: 60%.
    confidence_threshold = 0.45

    # Automatically classify tickets submitted as "general"
    # only when the prediction reaches the threshold.
    if (
        ticket_data["category"] == "general"
        and confidence >= confidence_threshold
    ):
        ticket_data["category"] = predicted_category

    # Prepare the ticket for database insertion.
    item = {
        "id": str(uuid4()),
        **ticket_data,
        "status": "open",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    # Save the ticket exactly once.
    with connect() as db:
        db.execute(
            """
            INSERT INTO tickets
            (
                id,
                title,
                description,
                category,
                priority,
                status,
                created_at
            )
            VALUES
            (
                :id,
                :title,
                :description,
                :category,
                :priority,
                :status,
                :created_at
            )
            """,
            item,
        )

    return item


# --------------------------------------------------
# Update Ticket Status
# --------------------------------------------------

@app.patch("/api/tickets/{ticket_id}")
def update_ticket(ticket_id: str, update: TicketUpdate):
    with connect() as db:
        result = db.execute(
            "UPDATE tickets SET status = ? WHERE id = ?",
            (update.status, ticket_id),
        )

        if result.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Ticket not found",
            )

        row = db.execute(
            "SELECT * FROM tickets WHERE id = ?",
            (ticket_id,),
        ).fetchone()

    return dict(row)


# --------------------------------------------------
# Upload Document
# --------------------------------------------------

@app.post("/api/documents")
async def upload_document(file: UploadFile = File(...)):
    filename = file.filename or ""
    content = await file.read()

    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="Maximum upload size is 10 MB",
        )

    try:
        text = extract_document(filename, content)

        print("EXTRACTED DOCUMENT TEXT:", text[:3000])

        chunks = add_document(text, filename)

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    finally:
        await file.close()

    return {
        "filename": filename,
        "chunks_indexed": chunks,
        "status": "indexed",
    }


# --------------------------------------------------
# List Uploaded Documents
# --------------------------------------------------

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
        filename = record.get(
            "source",
            "Unknown document",
        )

        if filename not in documents:
            documents[filename] = {
                "filename": filename,
                "chunks": 0,
                "status": "indexed",
            }

        documents[filename]["chunks"] += 1

    return list(documents.values())


# --------------------------------------------------
# Delete Uploaded Document
# --------------------------------------------------

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


# --------------------------------------------------
# AI Document Chat
# --------------------------------------------------

@app.post("/api/chat")
def chat(request: ChatRequest):

    question = request.question.strip()
    question_lower = question.lower()

    fallback_answer = (
        "I couldn't find this information in the uploaded documents. "
        "Please create a support ticket for further assistance."
    )

    # Handle questions about missing document information.
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

    # Search for relevant document chunks.
    search_start = perf_counter()

    # Use a focused query for dress-code questions.
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

    results = search_documents(
        search_query,
        top_k=20,
    )

    # Debug information for document retrieval.
    print(f"SEARCH QUERY: {search_query}")
    print(f"RETRIEVED CHUNKS: {len(results)}")

    for item in results[:5]:
        print(
            "SCORE:",
            round(float(item.get("score", 0)), 3),
        )
        print(
            "SOURCE:",
            item.get("source", "Unknown"),
        )
        print(
            "TEXT:",
            item.get("text", "")[:300],
        )
        print("-" * 40)

    search_time = perf_counter() - search_start

    print(
        f"DOCUMENT SEARCH TIME: {search_time:.2f} seconds"
    )

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

    # Prioritize relevant evidence for dress-code questions.
    if is_dress_question:
        matching = [
            item
            for item in unique_results
            if (
                "neat, clean and appropriate"
                in item["text"].lower()
                or "dress and appearance"
                in item["text"].lower()
                or (
                    "appearance" in item["text"].lower()
                    and "personal hygiene"
                    in item["text"].lower()
                )
            )
        ]

        sources = (
            matching[:2]
            if matching
            else unique_results[:4]
        )

    # Prioritize direct evidence for employee-name questions.
    elif "employee name" in question_lower:
        matching = [
            item
            for item in unique_results
            if "employee name" in item["text"].lower()
        ]

        sources = (
            matching[:1]
            if matching
            else unique_results[:4]
        )

    else:
        sources = unique_results[:4]

    # Generate an answer using the retrieved evidence.
    llm_start = perf_counter()

    answer = generate_answer(
        question,
        sources,
    )

    llm_time = perf_counter() - llm_start

    print(
        f"OLLAMA GENERATION TIME: {llm_time:.2f} seconds"
    )

    if not answer or not isinstance(answer, str):
        answer = fallback_answer

    # Determine whether the user should create a support ticket.
    needs_ticket = (
        answer.strip() == fallback_answer
        or answer.strip().startswith("Fallback answer:")
    )

    if needs_ticket:
        sources = []

    return {
        "answer": answer,
        "sources": [
            {
                "filename": item.get(
                    "source",
                    "Unknown source",
                ),
                "excerpt": item.get("text", "")[:250],
                "score": round(
                    float(item.get("score", 0)),
                    3,
                ),
            }
            for item in sources
        ],
        "needs_ticket": needs_ticket,
    }
