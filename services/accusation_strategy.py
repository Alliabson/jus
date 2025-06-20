def generate_accusation(document_text: str, area: str, model) -> str:
    prompt = f"""
    Como promotor de {area}, elabore uma estratégia de acusação com:
    
    1. 3 elementos do crime/ilícito
    2. Fundamentação legal (artigos)
    3. Prova necessária
    4. Jurisprudência de apoio
    
    Documento: {document_text[:15000]}
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        raise Exception(f"Falha ao gerar acusação: {str(e)}")
