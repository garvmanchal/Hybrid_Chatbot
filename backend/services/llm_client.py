import os
from dotenv import load_dotenv
from groq import Groq
from google import genai
from dataclasses import dataclass

load_dotenv()

MODEL_MAP = {
    'fast_model' : "gemini-2.5-flash",
    'balanced_model' : "openai/gpt-oss-20b",
    'long_context_model' : "gemini-2.5-flash",
    'strong_model_with_review' : "openai/gpt-oss-20b",
}


# API CLIENTS
gemini_api = os.getenv("GEMINI_API_KEY")
groq_api = os.getenv("GROQ_API_KEY")



gemini_client = genai.Client(
    api_key = gemini_api
    )

groq_client = Groq(
    api_key = groq_api
    )



print("GEMINI API KEY LOADED: ", bool(gemini_api))
print("GROQ API KEY LOADED: ", bool(groq_api))

# This dataclass is used to provide a clean and consistent structure for storing LLM responses

@dataclass
class LLMResult :
    text : str
    input_tokens : int
    output_tokens : int 
    raw : dict
    model_route : str
    estimated_cost_usd: float
    needs_human_review: bool   


# router 
def choose_route(prompt: str) -> str :
    prompt_lower = prompt.lower()

    # for strong task review 
    if any(word in prompt_lower for word in[
        "debug",
        "analyze", 
        "find bugs",
        "code review"
    ]) :
        return "strong_model_with_review"


    # for long context task
    if len(prompt) > 10000 :
        return "long_context_model"

    # for simple/fast tasks
    if any(word in prompt_lower for word in 
           [
               "hello", 
               "hi", 
               "simple",
               "quick"
           ]) :
        return "fast_model"

    return "balanced_model"

    
# llm call


async def call_llm(prompt : str):
    route = choose_route(prompt)

    model = MODEL_MAP[route]

    print("Selected route",route)
    print("Selected Model  ",model)

#    gemini

    if model.startswith("gemini"):  

        response = gemini_client.models.generate_content(
            model = model,
            contents = prompt

        )


        return LLMResult(
            text = response.text,
            input_tokens = 0,

            output_tokens = 0 ,

            raw = response.model_dump() if hasattr(response,"model_dump") else{},
            
            model_route= route,

            estimated_cost_usd=0.0,
            # hasattr means does this have this attribute ?  
            needs_human_review = (route == "strong_model_with_review" )

        )

#  GROQ

    elif model.startswith("openai/") or model.startswith("qwen/"):
        response = groq_client.chat.completions.create(
            model = model,

            messages = [
                {
                    "role" : "user",
                    "content" : prompt
                }
            ]
        )

        return LLMResult(
            text = response.choices[0].message.content,
            input_tokens=response.usage.prompt_tokens
            if response.usage 
            else 0,
            
            output_tokens = response.usage.completion_tokens
            if response.usage
            else 0,

            raw = response.model_dump()
            if hasattr(response, "model_dump")
            else{}, 

            model_route = route,

            estimated_cost_usd= 0.0,

            needs_human_review=(route == ("strong_model_with_review"))
        )
    
            

    else :
        raise ValueError(f"Unsupported Model : {model}")
    

