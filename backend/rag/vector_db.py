from backend.rag.embedding import embedding_text, cosine_sim

class InVectorDB:
    def __init__(self):
        self.rows : list[dict] = []

    # upsert refers to update and insert
    def upsert(self,chunk : dict):
        self.rows.append({**chunk, "vector" : embedding_text(chunk["text"])})
        
        '''
        **chunk means dictionary unpacking in this case.Take everything inside this dictionary and put it here."

        self.rows.append({**chunk,"vector": embed_text(chunk["text"])})
        This line means : 
        "Take all the information from chunk, and additionally add its embedding as vector."
        '''



    def search(self, query_vector : list[float], filters : dict, limit: int) ->list[dict]:
        candidates = [
            r for r in self.rows
            if r ["permission_scope"] in filters["permission_scope"]
            and r ["status"] == filters.get("status", "published")

        ]

        scored = sorted(candidates, key = lambda r : cosine_sim(query_vector, r["vector"]), reverse = True)
        return scored[:limit]

vector_db = InVectorDB()

'''
    Take the user's query vector → filter allowed documents → calculate similarity
      → sort by similarity → return the top results.

      filters.get("status", "published")
      this line means :
      Get "status" from filters. If it doesn't exist, use "published".


      cosine_sim(query_vector, r["vector"])
      means:
      Compare the user's query vector with the document's vector.

''' 