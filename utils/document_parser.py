import PyPDF2
from docx import Document
from typing import Union

def parse_legal_document(file) -> str:
    """Extrai texto de arquivos PDF ou DOCX"""
    if file.name.endswith('.pdf'):
        return extract_from_pdf(file)
    elif file.name.endswith('.docx'):
        return extract_from_docx(file)
    else:
        raise ValueError("Formato de arquivo não suportado")

def extract_from_pdf(file) -> str:
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def extract_from_docx(file) -> str:
    doc = Document(file)
    return "\n".join([para.text for para in doc.paragraphs])
