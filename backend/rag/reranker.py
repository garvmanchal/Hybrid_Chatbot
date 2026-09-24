from backend.rag.embedding import embedding_text , cosine_sim

async def re_rank(query : str, candidates: list[dict], keep : int = 15) -> list[dict]:
    query_vector = embedding_text(query) # user query vector

    for c in candidates:
        c["re_ranker_score"] = cosine_sim(query_vector, embedding_text(c["text"]))

    ranked = sorted(candidates, key = lambda c:c['re_ranker_score'], reverse =True)
    return ranked[:keep]


    '''
                                         user_query_vector       document vector
      c["re_ranker_score"] = cosine_sim( query_vector ,         embedding_text(c["text"])) 
        here we are comparing user query vector and document vector

        main purpose : 
        Search finds the relevant candidates → Reranking puts the best candidates first 
        → The LLM uses the top results to generate a better answer.

        The main purpose of rerank() is to reorder the retrieved candidate documents based on how
        semantically similar they are to the user's query, so that the most relevant documents appear at the top.

    '''  