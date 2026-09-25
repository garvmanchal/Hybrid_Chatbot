from typing import Optional

from fastapi import APIRouter, Form, File, UploadFile, HTTPException

from backend.services.chat_service import answer_question
from backend.rag.ingest import ingest_upload, UploadRejected


router = APIRouter(prefix= "/chat", tags= ["Chat"])


@router.post("/")
async def chat(
    question: str = Form(...),
    session_id: str = Form(...),
    file: Optional[UploadFile] = File(None),
):
    # Every session always gets the shared employee handbook scope, plus
    # its own private scope so anything it has uploaded is retrievable on
    # this and later questions in the same chat - and only in this chat.
    allowed_scopes = ["employee", f"session:{session_id}"]

    attachment = None

    if file is not None:
        data = await file.read()

        try:
            attachment = ingest_upload(
                filename=file.filename or "upload",
                content_type=file.content_type or "",
                data=data,
                session_id=session_id,
            )
        except UploadRejected as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    result = await answer_question(
        question=question,
        allowed_scopes=allowed_scopes,
    )

    if attachment is not None:
        result["attachment"] = attachment

    return result
