from datetime import date

from backend.rag.pdf_loader import load_pdf_bytes
from backend.rag.chunking import chunk_document
from backend.rag.vector_db import vector_db


# Mirrors the validation already done client-side in the React app.
# The backend must not trust the client, so the same rules are re-checked here.
ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "image/webp",
}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


class UploadRejected(Exception):
    """Raised when an attachment fails validation (bad type / too large)."""


def ingest_upload(
    filename: str,
    content_type: str,
    data: bytes,
    session_id: str,
) -> dict:
    """
    Validate an uploaded chat attachment and, if possible, extract its text,
    chunk it, embed it, and add it to the in-memory vector store so the
    current question (and any follow-up questions in the same chat session)
    can retrieve it through the normal hybrid_search path.

    The chunks are tagged with permission_scope = f"session:{session_id}" so
    one user's upload is never retrievable by another session, and so the
    shared Orion Employee Handbook index (permission_scope="employee") is
    left untouched.

    Returns a small dict describing what happened, meant to be surfaced to
    the frontend (e.g. "3 chunks indexed" or "images aren't searchable yet").
    """

    if content_type not in ALLOWED_CONTENT_TYPES:
        raise UploadRejected(
            f"Unsupported file type '{content_type}'. "
            "Only PDF, JPG, PNG and WEBP files are allowed."
        )

    if len(data) > MAX_FILE_SIZE:
        raise UploadRejected("File size must be less than 10 MB.")

    permission_scope = f"session:{session_id}"
    today = date.today().isoformat()

    if content_type == "application/pdf":
        pages = load_pdf_bytes(data)

        if not pages:
            return {
                "filename": filename,
                "indexed": False,
                "chunks_indexed": 0,
                "note": (
                    "No extractable text was found in this PDF "
                    "(it may be a scanned/image-only document)."
                ),
            }

        chunks_indexed = 0

        for page in pages:
            chunks = chunk_document(
                source_id=f"upload:{session_id}:{filename}",
                heading=filename,
                text=page["text"],
                permission_scope=permission_scope,
                updated_at=today,
                page=page["page"],
                content_type="upload",
            )

            for chunk in chunks:
                vector_db.upsert(chunk)
                chunks_indexed += 1

        return {
            "filename": filename,
            "indexed": chunks_indexed > 0,
            "chunks_indexed": chunks_indexed,
            "note": None,
        }

    # image/jpeg, image/png, image/webp: no OCR/vision pipeline is wired up
    # yet, so the file is accepted but not made searchable.
    return {
        "filename": filename,
        "indexed": False,
        "chunks_indexed": 0,
        "note": (
            "Image uploads aren't indexed for retrieval yet - "
            "only PDF text is searchable right now."
        ),
    }
