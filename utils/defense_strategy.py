import google.generativeai as genai

def generate_defense(document_text: str, area: str) -> str:
    """Gera estratégia de defesa baseada no documento"""
    prompt = f"""
    Como especialista em direito {area}, analise este caso e sugira uma estratégia de defesa:
    
    1. Identifique 3 pontos fracos na argumentação contrária
    2. Sugira 2 artigos de lei aplicáveis
    3. Recomende 3 ações processuais imediatas
    
    Documento: {document_text[:10000]}
    """
    
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt)
    return response.text
