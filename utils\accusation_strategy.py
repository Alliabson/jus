import google.generativeai as genai

def generate_accusation(document_text: str, area: str) -> str:
    """Gera estratégia de acusação baseada no documento"""
    prompt = f"""
    Como promotor especializado em {area}, desenvolva uma estratégia de acusação:
    
    1. Destaque 3 elementos que caracterizam o ilícito
    2. Liste dispositivos legais violados
    3. Proponha medidas para fortalecer a acusação
    
    Documento: {document_text[:10000]}
    """
    
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt)
    return response.text
