import pymupdf

def load_pdf(pdf_path : str ) -> list[dict] :
    document = pymupdf.open(pdf_path)

    pages = []

    for page_no, page in enumerate(document, start = 1) :
        text = page.get_text("text").strip()

        if not text :
            continue

        pages.append({
            "page" : page_no,
            "text" : text
        })

    document.close()

    return pages


if __name__ == "__main__":
        print("pdf loader started")

        pdf_path = "backend/data/Orion_Technologies_Employee_Handbook.pdf"

        pages = load_pdf(pdf_path)

        print("Total pages :",len(pages))

        for page in pages:
            print(f"\n ---PAGE{page['page']} ---")
            print(page["text"][:300])
    