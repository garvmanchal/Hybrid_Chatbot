
from fastapi import APIRouter
from pydantic import BaseModel

from backend.services.chat_service import answer_question


router = APIRouter(prefix= "/chat", tags= ["Chat"])

class ChatRequest(BaseModel):
    question : str

@router.post("/")
async def chat(request : ChatRequest):
    result = await answer_question(
        question = request.question,
        allowed_scopes=["employee"]
    )  

    return result 