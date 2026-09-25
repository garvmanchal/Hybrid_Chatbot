import json                                   # Used to convert JSON string ↔ Python dictionary.
import re                               # Python's regular expression library. Removing ```json wrappers from LLM responses.
                                                         # Finding citations like [C1], [C2].


from backend.rag.search import hybrid_search
from backend.rag.reranker import re_rank
from backend.rag.prompt import build_cited_prompt
from backend.services.llm_client import call_llm

def is_casual_message(question: str) -> bool:

    question = question.strip().lower()   #Normalize the question

    # Common casual/greeting words  // These are messages that don't need RAG.
    casual_words = [
        "hi",
        "hello",
        "hey",
        "hii",
        "hiii",
        "heyy",
        "yo",
        "bye",
        "goodbye",
        "thanks",
        "thank you",
    ]

    # Exact match
    if question in casual_words:
        return True

    # Greeting at the beginning of the sentence
    if question.startswith(("hi ", "hello ", "hey ")):
        return True

    # Common conversational phrases
    casual_phrases = [
        "how are you",
        "how r you",
        "how r u",
        "what's up",
        "whats up",
        "who are you",
        "what can you do",
        "i am feeling",
        "i'm feeling",
        "im feeling",
        "i feel",
        "feeling low",
        "feeling sad",
        "feeling good",
        "feeling happy",
        "feeling bad",
    ]

    for phrase in casual_phrases:
        if phrase in question:
            return True

    return False



async def answer_question( question: str, allowed_scopes: list[str]) -> dict:

    # ==========================================
    # 0. Handle casual conversation
    # ==========================================

    if is_casual_message(question):

        casual_prompt = f"""You are a friendly AI assistant.
             The user said:
            {question}

            Respond naturally and briefly.

            Do not mention the knowledge base.
            Do not use citations.
            Return ONLY valid JSON.

        Format:
            {{
                "answer": "your response",
                "citations": [],
                "needs_human_review": false
            }}
            """

        result = await call_llm(casual_prompt)

        raw_response = result.text.strip()

        # Remove markdown JSON wrapper if present
        if raw_response.startswith("```"):
            raw_response = re.sub(
                r"^```(?:json)?\s*",
                "",
                raw_response,
                flags=re.IGNORECASE
            )

            raw_response = re.sub(
                r"\s*```$",
                "",
                raw_response
            )

            raw_response = raw_response.strip()

        try:
            llm_response = json.loads(raw_response)

        except json.JSONDecodeError:
            llm_response = {
                "answer": raw_response,
                "citations": [],
                "needs_human_review": False
            }

        return {
            "answer": llm_response.get("answer", ""),
            "citations": [],
            "needs_human_review": False,
            "model_routing": result.model_route
        }


    # ==========================================
    # 1. Retrieve relevant chunks // "Give me the top 30 potentially relevant chunks.
    # ==========================================

    candidates = await hybrid_search(
        query=question,
        allowed_scopes=allowed_scopes,
        top_k=30
    )


    # ==========================================
    # 2. Rerank // we take 30 relevent chunks and then reduce it to 15 best chunks
    # ==========================================

    ranked_chunks = await re_rank(
        query=question,
        candidates=candidates,
        keep=15
    )


    # ==========================================
    # 3. Build RAG prompt  // This is where your retrieved knowledge becomes LLM context.
    # ==========================================

    prompt = build_cited_prompt(
        question=question,
        chunks=ranked_chunks
    )


    # ==========================================
    # 4. LLM  // Here your LLM generates the final answer for your RAG pipeline.
    # ==========================================

    result = await call_llm(prompt)
    print(result)


    # ==========================================
    # 5. Parse JSON
    # ==========================================

    raw_response = result.text.strip()

    if raw_response.startswith("```"):

        raw_response = re.sub(
            r"^```(?:json)?\s*",
            "",
            raw_response,
            flags=re.IGNORECASE
        )

        raw_response = re.sub(
            r"\s*```$",
            "",
            raw_response
        )

        raw_response = raw_response.strip()

#  For a normal RAG answer, invalid structured output is treated more seriously.

    try:

        llm_response = json.loads(raw_response)

    except json.JSONDecodeError:

        print("LLM returned invalid JSON:")
        print(raw_response)

        llm_response = {
            "answer": raw_response,
            "citations": [],
            "needs_human_review": True
        }


    # ==========================================
    # 6. Extract answer
    # ==========================================

    answer = llm_response.get(
        "answer",
        ""
    )


    # ==========================================
    # 7. Extract citations
    # ==========================================
    cited_labels = re.findall(
        r"\[C\d+\]",
        answer
    )

    cited_labels = list(
        dict.fromkeys(cited_labels)
    )

    '''
    Let's understand the regex.
    \[       → literal [
    C        → letter C
    \d+      → one or more digits
    \]       → literal ]
        
    '''


    # ==========================================
    # 8. Return
    # ==========================================

    return {
        "answer": answer,
        "citations": cited_labels,

        "needs_human_review":
            llm_response.get(
                "needs_human_review",
                len(ranked_chunks) == 0
            ),

        "model_routing":
            result.model_route
    }

