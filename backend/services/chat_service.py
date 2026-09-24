# from backend.rag.search import hybrid_search
# from backend.rag.reranker import re_rank
# from backend.rag.prompt import build_cited_prompt
# from backend.services.llm_client import call_llm



# async def answer_question(question : str, allowed_scopes:list[str]) -> dict:

#     # 1. Retrieve relevant chunks
#     candidates = await hybrid_search(query = question, allowed_scopes=allowed_scopes, top_k = 30)

#     # 2.  Rerank the retrieved chunks   
#     ranked_chunks = await re_rank(query = question , candidates = candidates, keep = 15)

#     # 3. Build grounded prompt
#     prompt = build_cited_prompt(question = question, chunks = ranked_chunks)

#     # 4. Send prompt to LLM  
#     result = await call_llm(prompt)

#     # 5. Return Chatbot response
#     return{
#         "answer": result.text,


#         "citations": [
#             chunk["citation_label"]
#             for chunk in ranked_chunks
#             if "citation_label" in chunk
#         ], 


#         "needs_human_review" : result.needs_human_review,
#         "model_route": result.model_route
#     }
import json
import re 
from backend.rag.search import hybrid_search
from backend.rag.reranker import re_rank
from backend.rag.prompt import build_cited_prompt
from backend.services.llm_client import call_llm


async def answer_question(
    question: str,
    allowed_scopes: list[str]
) -> dict:

    # 1. Retrieve relevant chunks
    candidates = await hybrid_search(
        query=question,
        allowed_scopes=allowed_scopes,
        top_k=30
    )

    # 2. Rerank retrieved chunks
    ranked_chunks = await re_rank(
        query=question,
        candidates=candidates,
        keep=15
    )

    # 3. Build grounded prompt
    prompt = build_cited_prompt(
        question=question,
        chunks=ranked_chunks
    )

    # 4. Send grounded prompt to LLM
    result = await call_llm(prompt)


    # 5. Parse LLM JSON 
    try:
        llm_response = json.loads(result.text)

    except json.JSONDecodeError:
        llm_response = {
            "answer": result.text,
            "citations": [],
            "needs_human_review": True
        }

    answer = llm_response.get("answer", "")

    # 6. Extract citations actually used in the answer
    cited_labels = re.findall(
        r"\[C\d+\]",
        answer
    )

    # Remove duplicates while preserving order
    cited_labels = list(dict.fromkeys(cited_labels))



    # 7. Return response
    return {
        "answer": llm_response.get("answer", ""),
        "citations": cited_labels,
        "needs_human_review": len(ranked_chunks) == 0,
        "model_route": result.model_route
    }