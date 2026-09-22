
def chunk_text(text : str , chunk_word : int = 60 , overlap_word : int = 15) -> list[dict]:
    words = text.split()
    chunks, start = [], 0
    while start < len(words):

        end = start +  chunk_word   
        chunks.append(" ".join(words[start:end]))
        start = end - overlap_word

    return chunks




def chunk_document(source_id : str, heading : str, text : str, permission_scope : str,
                 updated_at: str, content_type: str = "policy") -> list[dict]:

    pieces = chunk_text(text)

    return[{
        "chunk_id" : f"{source_id} - c{i}",
        "text" : piece,
        "source_id" : source_id,
        "heading" : heading,
        "permission_scope": permission_scope,
        "updated_at" : updated_at,
        "content_type" : content_type,
        "status" : "published"
    }

    for i, piece in enumerate(pieces)

    ]
