from PyPDF2 import PdfReader
from docx import Document

def parse_resume(file):
    if file.filename.endswith(".pdf"):
        reader = PdfReader(file.file)
        text = " ".join(page.extract_text() or "" for page in reader.pages)
    elif file.filename.endswith(".docx"):
        doc = Document(file.file)
        text = " ".join(p.text for p in doc.paragraphs)
    else:
        raise ValueError("Unsupported file format")

    return text.lower()
