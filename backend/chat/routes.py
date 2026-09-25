
from fastapi import APIRouter, Form,File, UploadFile


from backend.services.chat_service import answer_question


router = APIRouter(prefix= "/chat", tags= ["Chat"])


@router.post("/")
async def chat(question: str = Form(...),
               session_id : str = Form(...),
               file : UploadFile | None = File(None)
):

    result = await answer_question(question = question, allowed_scopes=['employee'])


    return result