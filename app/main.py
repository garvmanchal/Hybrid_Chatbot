from fastapi import FastAPI 
from app.services.llm_client import call_llm
from app.models.schemas import ChatRequest, ChatResponse
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title = "Hybrid Chatbot")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # your Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def show_root():
    return  {
        "message" : "This is my chatbot"
    }


@app.post("/chat", response_model = ChatResponse) 
# response_model = ChatResponse 
# This tells FastAPI:
# "The response coming from /chat must follow the ChatResponse schema."
async def chat(request : ChatRequest) :

    result = await call_llm(request.message)

    return ChatResponse(
        answer = result.text,
        model_route =  result.model_route,
        input_token =  result.input_tokens,
        output_token =  result.output_tokens,
        estimated_cost_usd = result.estimated_cost_usd, 
        needs_human_review = result.needs_human_review
    )

    
    