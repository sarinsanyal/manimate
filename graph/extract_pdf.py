import fitz  # PyMuPDF
from graph.state import GraphState

MAX_TOPICS = 6  # cap on how many topics segment_topics can pull from one PDF, tune as needed

def extract_pdf_node(state: GraphState) -> GraphState:
    pdf_path = state["pdf_path"]

    doc = fitz.open(pdf_path)
    pages_text = []
    for page in doc:
        text = page.get_text().strip()
        if text:
            pages_text.append(text)
    doc.close()

    full_text = "\n\n".join(pages_text)

    if not full_text.strip():
        raise ValueError(f"No extractable text found in {pdf_path}. It may be a scanned/image-only PDF.")

    print(f"  Extracted {len(pages_text)} pages, {len(full_text)} characters from {pdf_path}")

    return {**state, "raw_pdf_text": full_text}