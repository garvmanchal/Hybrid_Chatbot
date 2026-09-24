#Chunking : 
# chunking is a way of process in which it divide a large document into smaller peices called chunks , 
# which make it easier for the system to process, store , search , and retrieve releveant info


def chunk_text(text : str , chunk_word : int = 60 , overlap_word : int = 15) -> list[dict]:
    words = text.split()
    chunks, start = [], 0
    while start < len(words):

        end = start +  chunk_word    # Keep creating chunks as long as start hasn't reached the end of the words.
        chunks.append(" ".join(words[start:end])) # take the words from start up to end, join them into one string, and append that string to the chunks list.
        start = end - overlap_word

    return chunks

 
def chunk_document(source_id : str, heading : str, text : str, permission_scope : str,
                 updated_at: str,page : int,  content_type: str = "policy") -> list[dict]:

    pieces = chunk_text(text)

    return[{
        "chunk_id" : f"{source_id} -p{page} -c{i}",
        "text" : piece,
        "source_id" : source_id,
        "heading" : heading,
        "permission_scope": permission_scope,
        "updated_at" : updated_at,
        "content_type" : content_type,
        "status" : "published",
        "page" : page
    }

    for i, piece in enumerate(pieces) #Go through every item in pieces, and give me both its index (i) and its value (piece).

    ]
