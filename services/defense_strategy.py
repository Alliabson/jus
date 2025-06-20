# services/defense_strategy.py

# Se ainda não estiver importado, adicione:
import google.generativeai as genai

def generate_defense(document_text: str, area: str, contexto_estrategia: str, model: genai.GenerativeModel) -> str:
    """
    Gera uma estratégia de defesa com base no texto jurídico, área, contexto e usando um LLM.
    """
    # Ajustei o prompt para incorporar o contexto_estrategia
    # e especifiquei o tipo do modelo como genai.GenerativeModel para clareza (type hinting)
    
    prompt = f"""
    Como especialista em direito {area}, analise este caso e:

    1. Liste 3 vulnerabilidades na acusação.
    2. Sugira 2 artigos de lei aplicáveis.
    3. Recomende 3 ações processuais.
    4. Cite 1 jurisprudência favorável (se houver elementos no texto).

    Considere o seguinte ponto principal ou contexto adicional para a estratégia de defesa: "{contexto_estrategia if contexto_estrategia else 'Não há contexto adicional fornecido.'}"

    Documento para análise:
    {document_text[:15000]} # Limite de contexto para evitar sobrecarga do token

    Por favor, apresente a estratégia de forma clara, com tópicos e linguagem jurídica apropriada.
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        # É uma boa prática capturar exceções aqui e relançar uma exceção mais específica
        # ou retornar uma mensagem de erro tratada para o Streamlit.
        return f"Falha ao gerar defesa: {str(e)}"
