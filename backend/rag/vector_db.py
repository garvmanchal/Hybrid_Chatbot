from backend.rag.embedding import embedding_text, cosine_sim

class InVectorDB:
    def __init__(self):
        self.rows : list[dict] = []


    def upsert(self,chunk : dict):
        self.rows.append({**chunk, "vector" : embedding_text(chunk["text"])})


    def search(self, query_vector : list[float], filters : dict, limit: int) ->list[dict]:
        candidates = [
            r for r in self.rows
            if r ["permission_scope"] in filters["permission_scope"]
            and r ["status"] == filters.get("status", "published")

        ]

        scored = sorted(candidates, key = lambda r : cosine_sim(query_vector, r["vector"]), reverse = True)
        return sorted[:limit]

vector_db = InVectorDB()