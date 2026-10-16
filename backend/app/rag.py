import re
import json
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import (
    SentenceTransformer,
    CrossEncoder,
)

DATA = Path("data")
DATA.mkdir(exist_ok=True)

INDEX_FILE = DATA / "index.faiss"
CHUNKS_FILE = DATA / "chunks.json"

MIN_SCORE = 0.22
CANDIDATE_MULTIPLIER = 5
MIN_CANDIDATES = 20

# Embedding model for initial retrieval.
model = SentenceTransformer("all-MiniLM-L6-v2")

# CrossEncoder for reranking retrieved passages.
reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L6-v2")


def split_chunks(text, size=900, overlap=150):
    """Split document text into overlapping chunks."""

    if overlap >= size:
        raise ValueError("Overlap must be less than size")

    # Remove common PDF encoding-corruption sequences.
    text = re.sub(
        r"(?:ÃƒÆ’|Ãƒâ€š|Ã¢â‚¬Å¡|Ã¢â‚¬Å“|Ã¢â‚¬â„¢|Ã‚)+",
        " ",
        text,
    )

    # Normalize whitespace.
    text = " ".join(text.split())

    chunks = []

    for start in range(0, len(text), size - overlap):
        chunk = text[start : start + size].strip()

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

    if CHUNKS_FILE.exists():
        records = json.loads(CHUNKS_FILE.read_text(encoding="utf-8"))
    else:
        records = []

    existing_chunks = [
        record.get("text", "").strip()
        for record in records
        if record.get("source") == filename
    ]

    # Avoid re-indexing unchanged documents.
    if existing_chunks == chunks:
        print(f"DOCUMENT ALREADY INDEXED: {filename}")
        return 0

    # Remove old chunks for this document.
    updated_records = [record for record in records if record.get("source") != filename]

    # Add the latest chunks.
    updated_records.extend(
        {
            "text": chunk,
            "source": filename,
        }
        for chunk in chunks
    )

    all_texts = [record["text"] for record in updated_records]

    vectors = np.asarray(
        model.encode(
            all_texts,
            normalize_embeddings=True,
        ),
        dtype="float32",
    )

    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)

    faiss.write_index(
        index,
        str(INDEX_FILE),
    )

    CHUNKS_FILE.write_text(
        json.dumps(
            updated_records,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(f"DOCUMENT INDEXED: {filename} " f"({len(chunks)} chunks)")

    return len(chunks)


def delete_document(filename):
    """Remove a document and rebuild the FAISS index."""

    if not CHUNKS_FILE.exists():
        return 0

    records = json.loads(CHUNKS_FILE.read_text(encoding="utf-8"))

    remaining_records = [
        record for record in records if record.get("source") != filename
    ]

    removed_count = len(records) - len(remaining_records)

    if removed_count == 0:
        return 0

    if remaining_records:
        texts = [record["text"] for record in remaining_records]

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
        dimension = model.get_sentence_embedding_dimension()
        index = faiss.IndexFlatIP(dimension)

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

    print(f"DOCUMENT DELETED: {filename} " f"({removed_count} chunks removed)")

    return removed_count


def search_documents(question, top_k=4):
    """Retrieve candidate chunks and rerank them for relevance."""

    if not INDEX_FILE.exists() or not CHUNKS_FILE.exists():
        return []

    index = faiss.read_index(str(INDEX_FILE))

    records = json.loads(CHUNKS_FILE.read_text(encoding="utf-8"))

    if not records or index.ntotal == 0:
        return []

    # Encode the question for initial FAISS retrieval.
    query = np.asarray(
        model.encode(
            [question],
            normalize_embeddings=True,
        ),
        dtype="float32",
    )

    # Retrieve more candidates than the final requested count.
    candidate_count = min(
        max(top_k * CANDIDATE_MULTIPLIER, MIN_CANDIDATES),
        index.ntotal,
        len(records),
    )

    scores, ids = index.search(query, candidate_count)

    candidates = []
    seen = set()

    for score, chunk_id in zip(scores[0], ids[0]):
        if chunk_id < 0:
            continue

        score = float(score)

        # Keep the existing initial similarity threshold.
        if score < MIN_SCORE:
            continue

        record = records[int(chunk_id)]
        text = record.get("text", "").strip()
        filename = record.get("source", "Unknown source")

        # Remove duplicate chunks.
        key = (filename, text)

        if not text or key in seen:
            continue

        seen.add(key)

        candidates.append(
            {
                **record,
                "score": score,
            }
        )

    if not candidates:
        return []

    # Evaluate each question and candidate passage together.
    pairs = [[question, candidate["text"]] for candidate in candidates]

    rerank_scores = reranker.predict(pairs)

    for candidate, rerank_score in zip(
        candidates,
        rerank_scores,
    ):
        candidate["rerank_score"] = float(rerank_score)

    # Sort by CrossEncoder score, highest first.
    candidates.sort(
        key=lambda item: item["rerank_score"],
        reverse=True,
    )

    return candidates[:top_k]
