from fastapi import FastAPI 
# from backend.services.llm_client import call_llm
# from backend.models.schemas import ChatRequest, ChatResponse
from fastapi.middleware.cors import CORSMiddleware
from backend.chat.routes import router as chat_router
# from backend.rag.seed_index import seed_index


app = FastAPI(title = "Hybrid Chatbot")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # your Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# @app.on_event("startup")
# async def startup_event():
#     seed_index()

    
@app.get("/")
def show_root():
    return  {
        "message" : "This is my chatbot"
    }

# @app.post("/chat") 
# response_model = ChatResponse 
# This tells FastAPI:
# "The response coming from /chat must follow the ChatResponse schema."
# async def chat(request : ChatRequest) :

#     result = await call_llm(request.message)

    # return ChatResponse(
    #     answer = result.text,
    #     model_route =  result.model_route,
    #     input_token =  result.input_tokens,
    #     output_token =  result.output_tokens,
    #     estimated_cost_usd = result.estimated_cost_usd, 
    #     needs_human_review = result.needs_human_review
    # )

    

app.include_router(chat_router)