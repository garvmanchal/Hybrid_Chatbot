# 🤖 Hybrid Chatbot

A FastAPI-based hybrid LLM chatbot that intelligently routes user
prompts to different language models based on the type and complexity of
the request.

The project currently integrates **Google Gemini** and **Groq-hosted
models** and exposes a simple REST API for chatbot interactions.

## ✨ Features

-   🚀 FastAPI backend
-   🔀 Rule-based LLM routing
-   🤖 Google Gemini integration
-   ⚡ Groq integration
-   🧠 Different model routes for different task types
-   📝 Pydantic request/response validation
-   🌐 CORS support for a Vite/React frontend
-   🔍 Special routing for review/debugging tasks
-   📚 Long-context prompt detection
-   📊 Response metadata for model route, token usage, estimated cost,
    and human-review flag
-   🔐 Environment-variable based API key configuration

## 🏗️ Project Structure

``` text
Hybrid Chatbot/
│
├── app/
│   ├── main.py
│   │
│   ├── models/
│   │   └── schemas.py
│   │
│   └── services/
│       └── llm_client.py
│
├── .env
├── requirements.txt
└── README.md
```

## 🔄 How It Works

The application receives a user's message through the `/chat` endpoint.

``` text
User Prompt
    │
    ▼
FastAPI /chat
    │
    ▼
Prompt Router
    │
    ├── Review / Debug / Analyze
    │        ▼
    │   Strong Model + Human Review Flag
    │
    ├── Long Prompt
    │        ▼
    │   Long-Context Model
    │
    ├── Simple / Quick Prompt
    │        ▼
    │   Fast Model
    │
    └── Other Prompts
             ▼
       Balanced Model
             │
             ▼
        LLM Provider
             │
             ▼
        JSON Response
```

## 🧠 Model Routing

The router uses simple rules to select a model route.

  ----------------------------------------------------------------------------
  Route                        Condition               Provider
  ---------------------------- ----------------------- -----------------------
  `strong_model_with_review`   Review, debug, analyze, Groq
                               bug-finding, or         
                               code-review prompts     

  `long_context_model`         Prompt longer than      Gemini
                               10,000 characters       

  `fast_model`                 Simple/quick prompts    Gemini
                               such as greetings       

  `balanced_model`             Default route for other Groq
                               prompts                 
  ----------------------------------------------------------------------------

The model names are configured inside `app/services/llm_client.py`.

## 📡 API Endpoints

### `GET /`

Returns a basic health/message response.

Example:

``` json
{
  "message": "This is my chatbot"
}
```

### `POST /chat`

Sends a message to the chatbot.

#### Request

``` json
{
  "message": "Explain FastAPI in simple words",
  "risk": "low"
}
```

`risk` accepts:

-   `low`
-   `medium`
-   `high`

If it is omitted, the default value is `low`.

#### Response

``` json
{
  "answer": "FastAPI is a modern Python framework...",
  "model_route": "balanced_model",
  "input_token": 0,
  "output_token": 0,
  "estimated_cost_usd": 0.0,
  "needs_human_review": false
}
```

> Token counts and estimated cost are currently not fully implemented
> for Gemini responses, and cost is currently returned as `0.0`. These
> fields are part of the API design and can be extended later.

## 🛠️ Tech Stack

-   **Python**
-   **FastAPI**
-   **Pydantic**
-   **Google GenAI SDK**
-   **Groq SDK**
-   **Uvicorn**
-   **python-dotenv**
-   **React/Vite frontend compatible through CORS**

## ⚙️ Installation

### 1. Clone the repository

``` bash
git clone <your-repository-url>
cd "Hybrid Chatbot"
```

### 2. Create a virtual environment

Windows:

``` bash
python -m venv venv
venv\Scripts\activate
```

macOS/Linux:

``` bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

``` bash
pip install -r requirements.txt
```

## 🔑 Environment Variables

Create a `.env` file in the project root:

``` env
GEMINI_API_KEY=your_gemini_api_key
GROQ_API_KEY=your_groq_api_key
```

**Never commit your real API keys to GitHub.**

Add this to `.gitignore`:

``` gitignore
.env
venv/
__pycache__/
*.pyc
```

If an API key has already been committed or exposed, revoke/rotate it
and replace it with a new key.

## ▶️ Run the Application

From the project root:

``` bash
uvicorn app.main:app --reload
```

The API will normally be available at:

``` text
http://127.0.0.1:8000
```

FastAPI's interactive documentation is available at:

``` text
http://127.0.0.1:8000/docs
```

You can also view the OpenAPI schema at:

``` text
http://127.0.0.1:8000/redoc
```

## 🧪 Testing the API

Using `curl`:

``` bash
curl -X POST "http://127.0.0.1:8000/chat" ^
  -H "Content-Type: application/json" ^
  -d "{\"message\":\"Hello, how are you?\",\"risk\":\"low\"}"
```

Or use the interactive Swagger UI:

``` text
http://127.0.0.1:8000/docs
```

## 🌐 Frontend Integration

The backend currently allows requests from:

``` text
http://localhost:5173
```

This makes it suitable for connecting to a React/Vite frontend.

Example frontend request:

``` javascript
const response = await fetch("http://127.0.0.1:8000/chat", {
  method: "POST",
  headers: {
    "Content-Type": "application/json"
  },
  body: JSON.stringify({
    message: userMessage,
    risk: "low"
  })
})

const data = await response.json()
```

## 🧩 Core Components

### `app/main.py`

Responsible for:

-   Creating the FastAPI application
-   Configuring CORS
-   Defining API endpoints
-   Calling the LLM service
-   Returning validated `ChatResponse` objects

### `app/models/schemas.py`

Contains Pydantic models:

-   `ChatRequest`
-   `ChatResponse`

These models validate API input and output.

### `app/services/llm_client.py`

Contains the main LLM logic:

-   API client initialization
-   Model configuration
-   Prompt routing
-   Gemini calls
-   Groq calls
-   Standardized `LLMResult` responses

## 🚧 Current Limitations

This project is an early implementation of a hybrid LLM routing system.

Current limitations include:

-   Routing is rule-based rather than ML-based.
-   Token usage is not currently populated for Gemini responses.
-   Estimated cost is currently `0.0`.
-   The `risk` request field is validated but is not currently used by
    the router.
-   Human review is represented by a boolean flag; there is no actual
    human-review workflow yet.
-   No conversation/database persistence is implemented.
-   No authentication or rate limiting is implemented.
-   Error handling and provider fallback can be expanded.
-   Model selection is currently configured directly in the Python
    source.

## 🚀 Future Improvements

Possible next steps:

1.  Add automatic provider fallback if one API fails.
2.  Implement accurate token and cost tracking for every provider.
3.  Use the `risk` field in routing decisions.
4.  Add conversation/session memory.
5.  Add authentication and rate limiting.
6.  Add structured logging and monitoring.
7.  Add automated evaluation of routing quality.
8.  Add retry and timeout handling.
9.  Move model configuration to environment/config files.
10. Build a production-ready React frontend.
11. Add human-in-the-loop review workflows.
12. Add unit and integration tests.

## 🎯 Learning Goals

This project demonstrates practical concepts involved in building
production-oriented LLM applications:

-   API development with FastAPI
-   Pydantic schema validation
-   Multi-provider LLM integration
-   Model routing
-   Prompt classification
-   Async API design
-   Environment-based secret management
-   Frontend/backend integration
-   AI application architecture

## 📄 License

This project is intended for learning and development purposes. Add a
license here if you plan to distribute the project publicly.
