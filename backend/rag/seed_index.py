# from backend.rag.pdf_loader import load_pdf
# from backend.rag.chunking import chunk_document
# from backend.rag.vector_db import vector_db 


# PDF_PATH = "backend/data/Orion_Technologies_Employee_Handbook.pdf"


# def seed_index():
#     print("Starting RAG indexing...")

#     pages = load_pdf(PDF_PATH)

#     print(f"loaded {len(pages)} pages")

#     total_chunks = 0 

#     for page in pages:
#         chunks = chunk_document(
#             source_id = "orion_employee_handbook",
#             heading = "Orion Technologies Employee Handbook",
#             text = page["text"],
#             permission_scope = "employee",
#             updated_at = "2026-09-24",
#             page = page['page'],
#             content_type = "policy"
#         )

#         for chunk in chunks:
#             vector_db.upsert(chunk)
#             total_chunks += 1


#         print(f"Indexed {total_chunks}chunks")
#         print(f"Vector DB contains {len(vector_db.rows)}chunks")
