# services/accusation_strategy.py

# Add this import if it's not already there
import google.generativeai as genai

def generate_accusation(document_text: str, area: str, contexto_estrategia: str, model: genai.GenerativeModel) -> str:
    """
    Gera uma estratégia de acusação com base no texto jurídico, área, contexto e usando um LLM.
    """
    # Adjusted the prompt to incorporate contexto_estrategia
    prompt = f"""
    Como promotor de {area}, analise este caso e elabore uma estratégia de acusação com:

    1. 3 elementos do crime/ilícito.
    2. Fundamentação legal (artigos) aplicáveis à acusação.
    3. Prova necessária para sustentar a acusação.
    4. Jurisprudência de apoio para a tese da acusação (se houver elementos no texto ou se for uma busca geral).

    Considere o seguinte ponto principal ou contexto adicional para a estratégia de acusação: "{contexto_estrategia if contexto_estrategia else 'Não há contexto adicional fornecido.'}"

    Documento para análise:
    {document_text[:15000]} # Limit context to avoid token overload

    Por favor, apresente a estratégia de forma clara, com tópicos e linguagem jurídica apropriada.
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        # It's good practice to return a user-friendly message or re-raise a specific exception
        return f"Falha ao gerar acusação: {str(e)}"
