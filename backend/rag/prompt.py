def build_cited_prompt(question: str, chunks: list[dict]) -> str:

    lines = []

    for i, chunk in enumerate(chunks, start=1):

        label = f"C{i}"

        chunk["citation_label"] = label

        lines.append(
            f"[{label}] "
            f"({chunk['heading']}, "
            f"updated {chunk['updated_at']}, "
            f"page {chunk.get('page', 'Unknown')}) "
            f"{chunk['text']}"
        )

    evidence = "\n".join(lines)

    return (
    "Answer using only the evidence below.\n"
    "Cite every factual sentence with its citation label.\n"
    "Do not use outside knowledge or invent information.\n"
    "If the evidence does not answer the question, "
    "say that the information was not found in the "
    "available knowledge base and set needs_human_review to true.\n\n"

    f"Evidence:\n{evidence}\n\n"

    f"Question: {question}\n\n"

    "Return JSON only: "
    '{"answer": "...", '
    '"citations": ["C1"], '
    '"needs_human_review": false}'
)