import PyPDF2
from docx import Document
from io import BytesIO

def parse_legal_document(file) -> str:
    """Extrai texto de arquivos PDF ou DOCX"""
    try:
        if file.name.endswith('.pdf'):
            return _extract_from_pdf(file)
        elif file.name.endswith('.docx'):
            return _extract_from_docx(file)
        else:
            raise ValueError("Formato de arquivo não suportado")
    except Exception as e:
        raise Exception(f"Falha ao extrair texto: {str(e)}")

def _extract_from_pdf(file) -> str:
    text = ""
    try:
        reader = PyPDF2.PdfReader(BytesIO(file.read()))
        for page in reader.pages:
            text += page.extract_text() or ""
    except Exception as e:
        raise Exception(f"Erro no PDF: {str(e)}")
    return text

def _extract_from_docx(file) -> str:
    try:
        doc = Document(BytesIO(file.read()))
        return "\n".join([para.text for para in doc.paragraphs if para.text])
    except Exception as e:
        raise Exception(f"Erro no DOCX: {str(e)}")
