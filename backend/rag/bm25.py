from backend.rag.vector_db import vector_db
from backend.rag.embedding import embedding_text

'''
bm25 search is type of keyword based search algorithm used to find documents/chunks that are most
relevent to a user's query
'''

def bm25_search(query : str, filters : dict, limit : int) -> list[dict]:

    q_terms = set(query.lower().split())

    candidates = [
        r for r in vector_db.rows
        if r ["permission_scope"] in filters["permission_scope"]
        and r ["status"] == filters.get("status", "published")

    ]
    '''
    the below code says :   
    Look at every candidate document, 
    count how many words from the query appear in it, give it a score, sort by score, and return the best ones.

    q_terms & document_terms : 
    The & between two sets means intersection.
    It finds the words that exist in both sets.

    The _ in return means:
    I don't care about this value.
    '''
    scored =[]

    for r in candidates :
         # Count matching words
        overlap = len(q_terms & set(r['text'].lower().split()))

    # Ignore documents with no matching words
        if overlap :
            scored.append((overlap,r))

        # Highest score first
    scored.sort(key = lambda pair:pair[0], reverse = True)
    # Return only the documents, not their scores
    return [r for _, r in scored[:limit]]


# Its job is to take two ranked result lists—keyword/BM25 results and vector-search results—and create one combined ranking.
# k is a constant used in the RRF formula. 
def reciprocal_rank_fusion(bm25_ranked : list[dict], vector_ranked : list[dict], k : int= 60) -> list[dict] :
    # This dictionary will store the combined RRF score for every chunk.
    scores : dict[str, float] = {}

    # This dictionary stores the actual chunk using its chunk_id.
    by_id ={}

    '''
    scores.get(chunk["chunk_id"], 0)
    This means:
    Get the current score for this chunk. If it doesn't exist yet, use 0.
    '''
    for rank, chunk in enumerate(bm25_ranked):
        scores[chunk["chunk_id"]] = scores.get(chunk["chunk_id"], 0) + 1 / (k + rank + 1)
        by_id[chunk["chunk_id"]] = chunk

    '''
    enumerate() is a built-in Python function that lets you loop through a list
      while getting both the index (position) and the item at the same time
    '''

    ranked_ids = sorted(scores.items(), key = lambda pair:pair[1], reverse = True)
    return [by_id[cid] for cid, _ in ranked_ids]


async def hybrid_search(query: str, allowed_scopes : list[str], top_k : int = 30) ->list[dict]:
    filters = {"permission_scope": allowed_scopes, "status" : "published"}
    query_vector = embedding_text(query)
    vector_results = vector_db.search(query_vector, filters, limit = 30)
    bm25_results = bm25_search(query, filters, limit = 30)
    fused = reciprocal_rank_fusion(bm25_results, vector_results)
    return fused[:top_k]  