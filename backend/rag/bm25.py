from backend.rag.vector_db import vector_db
from backend.rag.embedding import embedding_text


def bm25_search(query : str, filters : dict, limit : int) -> list[dict]:

    q_terms = set(query.lower().split())

    candidates = [
        r for r in vector_db.rows
        if r ["permission_scope"] in filters["permission_scope"]
        and r ["status"] == filters.get("status", "published")

    ]

    scored =[]

    for r in candidates :
        overlap = len(q_terms & set(r['text'].lower().split()))

        if overlap :
            scored.append((overlap,r))


    scored.sort(key = lambda pair:pair[0], reverse = True)
    return [r for _, r in scored[:limit]]


def reciprocal_rank_fusion(bm25_ranked : list[dict], vector_ranked : list[dict], k : int= 60) -> list[dict] :
    scores : dict[str, float] = {}

    by_id ={}

    for rank, chunk in enumerate(bm25_ranked):
        scores[chunk["chunk_id"]] = scores.get(chunk["chunk_id"], 0) + 1 / (k + rank + 1)
        by_id[chunk["chunk_id"]] = chunk


    ranked_ids = sorted(scores.items(), key = lambda pair:pair[1], reverse = True)
    return [by_id[cid] for cid, _ in ranked_ids]


async def hybrid_search(query: str, allowed_scopes : list[str], top_k : int = 30) ->list[dict]:
    filters = {"permission_scope": allowed_scopes, "status" : "published"}
    query_vector = embedding_text(query)
    vector_results = vector_db.search(query_vector, filters, limit = 30)
    bm25_results = bm25_search(query, filters, limit = 30)
    fused = reciprocal_rank_fusion(bm25_results, vector_results)
    return fused[:top_k]  