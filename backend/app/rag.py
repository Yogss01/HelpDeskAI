
import json
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


DATA = Path("data")
DATA.mkdir(exist_ok=True)

INDEX_FILE = DATA / "index.faiss"
CHUNKS_FILE = DATA / "chunks.json"

MIN_SCORE = 0.22

model = SentenceTransformer("all-MiniLM-L6-v2")


def split_chunks(text, size=900, overlap=150):
    """Split document text into overlapping chunks."""

    if overlap >= size:
        raise ValueError("Overlap must be less than size")

    text = " ".join(text.split())
    chunks = []

    for start in range(0, len(text), size - overlap):
        chunk = text[start:start + size].strip()

        if chunk:
            chunks.append(chunk)

        if start + size >= len(text):
            break

    return chunks



def add_document(text, filename):
    """Add or replace a document and rebuild the FAISS index."""

    chunks = split_chunks(text)

    if not chunks:
        return 0

    # Load existing document records.
    if CHUNKS_FILE.exists():
        records = json.loads(
            CHUNKS_FILE.read_text(encoding="utf-8")
        )
    else:
        records = []

    # Get the existing chunks for this filename.
    existing_chunks = [
        record.get("text", "").strip()
        for record in records
        if record.get("source") == filename
    ]

    # Skip indexing if the document content has not changed.
    if existing_chunks == chunks:
        print(f"DOCUMENT ALREADY INDEXED: {filename}")
        return 0

    # Remove all old chunks belonging to this filename.
    updated_records = [
        record
        for record in records
        if record.get("source") != filename
    ]

    # Add the latest chunks for this filename.
    updated_records.extend(
        {
            "text": chunk,
            "source": filename,
        }
        for chunk in chunks
    )

    # Rebuild the FAISS index from all remaining records.
    all_texts = [
        record["text"]
        for record in updated_records
    ]

    vectors = np.asarray(
        model.encode(
            all_texts,
            normalize_embeddings=True,
        ),
        dtype="float32",
    )

    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)

    # Save the rebuilt index.
    faiss.write_index(
        index,
        str(INDEX_FILE),
    )

    # Save the updated records.
    CHUNKS_FILE.write_text(
        json.dumps(
            updated_records,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(
        f"DOCUMENT INDEXED: {filename} "
        f"({len(chunks)} chunks)"
    )

    return len(chunks)


def delete_document(filename):
    """Remove a document and rebuild the FAISS index."""

    if not CHUNKS_FILE.exists():
        return 0

    records = json.loads(
        CHUNKS_FILE.read_text(encoding="utf-8")
    )

    # Remove every chunk belonging to this filename.
    remaining_records = [
        record
        for record in records
        if record.get("source") != filename
    ]

    removed_count = len(records) - len(remaining_records)

    # Return zero if the document was not found.
    if removed_count == 0:
        return 0

    # Rebuild the FAISS index using the remaining chunks.
    if remaining_records:
        texts = [
            record["text"]
            for record in remaining_records
        ]

        vectors = np.asarray(
            model.encode(
                texts,
                normalize_embeddings=True,
            ),
            dtype="float32",
        )

        index = faiss.IndexFlatIP(vectors.shape[1])
        index.add(vectors)

    else:
        # Keep a valid empty index if no chunks remain.
        dimension = model.get_sentence_embedding_dimension()
        index = faiss.IndexFlatIP(dimension)

    # Save the rebuilt index and remaining records.
    faiss.write_index(
        index,
        str(INDEX_FILE),
    )

    CHUNKS_FILE.write_text(
        json.dumps(
            remaining_records,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(
        f"DOCUMENT DELETED: {filename} "
        f"({removed_count} chunks removed)"
    )

    return removed_count


def search_documents(question, top_k=4):
    """Return the highest-scoring chunks above the minimum score."""

    if not INDEX_FILE.exists() or not CHUNKS_FILE.exists():
        return []

    index = faiss.read_index(str(INDEX_FILE))

    records = json.loads(
        CHUNKS_FILE.read_text(encoding="utf-8")
    )

    if not records or index.ntotal == 0:
        return []

    query = np.asarray(
        model.encode(
            [question],
            normalize_embeddings=True,
        ),
        dtype="float32",
    )

    search_count = min(
        max(top_k, 1),
        index.ntotal,
        len(records),
    )

    scores, ids = index.search(query, search_count)

    results = []
    seen = set()

    for score, chunk_id in zip(scores[0], ids[0]):
        if chunk_id < 0:
            continue

        score = float(score)

        # Ignore chunks below the initial relevance threshold.
        if score < MIN_SCORE:
            continue

        record = records[int(chunk_id)]
        text = record.get("text", "").strip()
        filename = record.get("source", "Unknown source")

        # Remove duplicate chunks from the results.
        key = (filename, text)

        if not text or key in seen:
            continue

        seen.add(key)

        results.append(
            {
                **record,
                "score": score,
            }
        )

    return results
