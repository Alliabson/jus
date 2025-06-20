def generate_defense(document_text: str, area: str, model) -> str:
    prompt = f"""
    Como especialista em direito {area}, analise este caso e:
    
    1. Liste 3 vulnerabilidades na acusação
    2. Sugira 2 artigos de lei aplicáveis
    3. Recomende 3 ações processuais
    4. Cite 1 jurisprudência favorável
    
    Documento: {document_text[:15000]}  # Limite de contexto
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        raise Exception(f"Falha ao gerar defesa: {str(e)}")
