import streamlit as st
import google.generativeai as genai
import sys
from pathlib import Path
import traceback
import os
from dotenv import load_dotenv

# --- CONFIGURAÇÃO DA PÁGINA (DEVE SER A PRIMEIRA CHAMADA STREAMLIT) ---
st.set_page_config(page_title="Assistente Jurídico IA", layout="wide", initial_sidebar_state="expanded")
# --- FIM DA CONFIGURAÇÃO DA PÁGINA ---

# Configura caminhos para que os módulos em 'utils' e 'services' possam ser importados
# Isso é essencial quando a estrutura do projeto é modular.
sys.path.append(str(Path(__file__).parent))

# Tenta importar os módulos. Se houver algum erro, exibe uma mensagem e para o app.
try:
    from utils.document_parser import parse_legal_document
    from utils.legal_api import fetch_jurisprudence
    from services.defense_strategy import generate_defense
    from services.accusation_strategy import generate_accusation
except ImportError as e:
    st.error(f"Erro de importação de módulo: {str(e)}")
    st.info("Verifique se os arquivos nas pastas 'utils' e 'services' existem e se seus nomes estão corretos.")
    st.info(f"O problema pode estar no módulo: {e.name}")
    st.stop()

# --- BLOCÔNICO DE CONFIGURAÇÃO DA CHAVE DE API DO GOOGLE GEMINI ---
API_KEY = None
try:
    # Tenta carregar a chave do Streamlit Secrets (ideal para Streamlit Cloud)
    # st.secrets é um dicionário, e "GOOGLE_API_KEY" é o NOME da chave que você configurou.
    API_KEY = st.secrets["GOOGLE_API_KEY"]
except KeyError:
    # Se não estiver em st.secrets (ex: rodando localmente), tenta carregar do arquivo .env
    load_dotenv() # Carrega as variáveis do arquivo .env da raiz do projeto
    # os.getenv() pega o valor da variável de ambiente com o NOME especificado.
    API_KEY = os.getenv("GOOGLE_API_KEY")

# Verifica se a chave foi carregada. Se não, exibe um erro e impede o app de rodar.
if not API_KEY:
    st.error("Erro crítico: A chave da API do Google Gemini não foi encontrada.")
    st.error("Por favor, configure-a corretamente:")
    st.error("- **No Streamlit Cloud:** Vá em 'Manage app' -> 'Secrets' e adicione `GOOGLE_API_KEY=\"SUA_CHAVE_AQUI\"`")
    st.error("- **Localmente:** Crie um arquivo `.env` na raiz do seu projeto com `GOOGLE_API_KEY=\"SUA_CHAVE_AQUI\"`")
    st.stop() # Interrompe a execução do Streamlit se a chave não for encontrada

# Configura o SDK do Google Gemini com a chave de API
genai.configure(api_key=API_KEY)
# Define o modelo de IA a ser usado. 'gemini-1.5-flash' é rápido e econômico.
model = genai.GenerativeModel('gemini-1.5-flash')
# --- FIM DO BLOCÔNICO DE CONFIGURAÇÃO ---


def main():
    # Título principal do aplicativo na página
    st.title("🤖 Assistente Jurídico Inteligente")

    # Sidebar para configurações globais do aplicativo
    with st.sidebar:
        st.header("Configurações")
        area_juridica = st.selectbox("Área Jurídica", ["Civil", "Criminal", "Previdenciário", "Outra"])
        tipo_acao = st.radio("Tipo de Ação", ["Defesa", "Acusação"])
        contexto_estrategia = st.text_area(
            "Contexto ou Ponto Principal da Estratégia (opcional):",
            "Ex: 'foco na ausência de provas', 'alegar cerceamento de defesa'"
        )

    # Criação de abas para organizar o conteúdo do aplicativo
    tab1, tab2, tab3 = st.tabs(["Análise e Upload", "Estratégia e Argumentos", "Legislação e Jurisprudência"])

    # --- Aba 1: Análise e Upload de Documentos ---
    with tab1:
        st.subheader("1. Carregue e Analise a Peça Jurídica")
        uploaded_file = st.file_uploader("Carregue a peça jurídica", type=["pdf", "docx"])
        document_text_input = st.text_area("Ou cole o texto da peça jurídica aqui (se preferir ou para testes rápidos):", height=300)

        # Lógica para determinar qual texto usar (upload ou cola)
        if uploaded_file:
            try:
                # Prioriza o upload de arquivo se houver
                text_from_file = parse_legal_document(uploaded_file)
                st.session_state.document_text = text_from_file
                st.success("Documento processado do arquivo com sucesso!")
                with st.expander("Visualizar texto extraído do arquivo"):
                    st.text(text_from_file[:5000] + ("..." if len(text_from_file) > 5000 else "")) # Limita exibição para não sobrecarregar
            except Exception as e:
                st.error(f"Erro ao processar documento carregado: {str(e)}")
                st.info("Certifique-se de que o arquivo PDF/DOCX está bem formatado e não está corrompido.")
                st.exception(e) # Exibe o traceback completo para depuração
        elif document_text_input: # Se não houver upload, usa o texto colado
            st.session_state.document_text = document_text_input
            st.success("Texto colado processado com sucesso!")
            with st.expander("Visualizar texto colado"):
                st.text(document_text_input[:5000] + ("..." if len(document_text_input) > 5000 else ""))
        
        # Verifica se há texto disponível para análise pela IA
        if 'document_text' in st.session_state and st.session_state.document_text:
            st.markdown("---")
            st.subheader("Análise Preliminar do Documento (IA)")
            if st.button("Analisar Texto com IA"):
                with st.spinner("A IA está analisando o texto... Isso pode levar alguns segundos."):
                    try:
                        # Prompt para a análise do documento pela IA
                        prompt_analise = f"""
                        Analise o seguinte texto jurídico. Identifique as seguintes informações:
                        1. Um breve resumo do conteúdo (máximo 5 frases).
                        2. O(s) ramo(s) do direito mais provável(is) (Ex: Civil, Criminal, Previdenciário, Administrativo, etc.).
                        3. Os 5-7 pontos mais importantes ou palavras-chave relevantes (entidades, conceitos-chave).
                        4. As partes envolvidas (Requerente/Autor, Requerido/Réu, etc.).
                        5. O objetivo principal da peça (Ex: Cobrança, Defesa, Recurso, etc.).

                        Formate a resposta de forma clara e com tópicos (use Markdown para negrito e listas):
                        **Resumo:** [Seu resumo aqui]
                        **Ramo(s) do Direito:** [Ramo1, Ramo2]
                        **Pontos Chave:** [ponto1, ponto2, ponto3, ...]
                        **Partes Envolvidas:** [Parte A: Nome, Parte B: Nome]
                        **Objetivo da Peça:** [Objetivo]

                        Texto para análise:
                        {st.session_state.document_text}
                        """
                        response = model.generate_content(prompt_analise)
                        st.markdown(response.text) # Usa markdown para formatar a resposta da IA

                    except Exception as e:
                        st.error(f"Erro ao gerar análise da IA: {str(e)}")
                        st.info("Verifique se o texto é legível e se há conectividade com a API do Gemini. Tente reduzir o tamanho do texto se for muito longo.")
                        st.exception(e)
        else:
            st.info("Carregue ou cole um documento para iniciar a análise.")

    # --- Aba 2: Geração de Estratégia e Argumentos ---
    with tab2:
        st.subheader("2. Geração de Estratégia e Argumentos")
        if 'document_text' not in st.session_state or not st.session_state.document_text:
            st.warning("Por favor, carregue ou cole um documento na aba 'Análise e Upload' primeiro para gerar uma estratégia.")
        else:
            st.info(f"Gerando estratégia para **{tipo_acao}** na área **{area_juridica}**.")
            st.write("Considerando o texto da peça jurídica e o contexto fornecido.")

            if st.button(f"Gerar Estratégia de {tipo_acao}"):
                with st.spinner(f"A IA está formulando a estratégia de {tipo_acao}... Isso pode levar alguns segundos."):
                    try:
                        # Chama as funções dos módulos 'services' para gerar a estratégia
                        if tipo_acao == "Defesa":
                            strategy = generate_defense(st.session_state.document_text, area_juridica, contexto_estrategia, model)
                        else: # Acusação
                            strategy = generate_accusation(st.session_state.document_text, area_juridica, contexto_estrategia, model)

                        st.subheader(f"Estratégia de {tipo_acao} Recomendada pela IA:")
                        st.markdown(strategy) # Usa markdown para formatar a resposta da IA

                    except Exception as e:
                        st.error(f"Erro ao gerar estratégia de {tipo_acao}: {str(e)}")
                        st.info("Verifique a qualidade do texto e do prompt. Tente novamente.")
                        st.exception(e)

    # --- Aba 3: Busca de Legislação e Jurisprudência ---
    with tab3:
        st.subheader("3. Busca de Legislação e Jurisprudência")

        # Seção para buscar Legislação (usando o Gemini como exemplo, para uma API real seria diferente)
        search_term_legis = st.text_input("Buscar Legislação (ex: 'Lei 8.213/91', 'Código Civil Art. 421')", key="legis_search")
        if st.button("Buscar Legislação (Exemplo via IA)", key="btn_legis_search"):
            if search_term_legis:
                with st.spinner(f"Buscando legislação para '{search_term_legis}'..."):
                    try:
                        legis_prompt = f"""
                        Com base na legislação brasileira, forneça informações sobre: {search_term_legis}.
                        Inclua o número da lei, artigo(s) relevante(s) e um breve resumo.
                        Se não for uma lei específica, forneça conceitos gerais relacionados ao termo.
                        Forneça a resposta em Português-BR.
                        """
                        response_legis = model.generate_content(legis_prompt)
                        st.subheader(f"Legislação Encontrada para '{search_term_legis}' (Via IA):")
                        st.markdown(response_legis.text)
                    except Exception as e:
                        st.error(f"Erro ao buscar legislação com IA: {str(e)}")
                        st.exception(e)
            else:
                st.warning("Por favor, digite um termo para buscar legislação.")

        st.markdown("---")

        # Seção para buscar Jurisprudência (usando o mock/API que você configurará em utils/legal_api.py)
        search_term_juris = st.text_input("Buscar Jurisprudência (ex: 'danos morais', 'responsabilidade civil')", key="juris_search")
        if st.button("Buscar Jurisprudência Externa", key="btn_juris_search"):
            if search_term_juris:
                with st.spinner(f"Buscando jurisprudência para '{search_term_juris}' na área '{area_juridica}'..."):
                    try:
                        # Chama a função do seu utils/legal_api.py (que ainda é um mock ou sua API real)
                        results = fetch_jurisprudence(search_term_juris, area_juridica)
                        if results and not results.get("error"):
                            st.subheader(f"Resultados da Jurisprudência para: '{results.get('termo', search_term_juris)}'")
                            if results['resultados']:
                                for res in results['resultados']:
                                    st.json(res) # Exibe o resultado como JSON formatado
                            else:
                                st.info("Nenhum resultado de jurisprudência encontrado para o termo especificado.")
                        else:
                            st.error("Não foi possível buscar a jurisprudência. Verifique os logs e a configuração da API externa.")
                            if results and "error" in results:
                                st.code(results["error"])
                    except Exception as e:
                        st.error(f"Erro na busca de jurisprudência: {str(e)}")
                        st.exception(e)
            else:
                st.warning("Por favor, digite um termo para buscar jurisprudência.")

# Disclaimer final do aplicativo
st.markdown("---")
st.caption("⚠️ **Atenção:** Este aplicativo utiliza inteligência artificial e serve apenas como uma ferramenta de **assistência**. As informações geradas não constituem aconselhamento jurídico e devem ser sempre revisadas e validadas por um profissional do direito qualificado.")
st.caption("A busca de jurisprudência externa é uma simulação. Para uso real, configure a URL e os parâmetros de uma API jurídica pública (ex: TJDFT, CNJ DataJud) ou paga.")

# Ponto de entrada do aplicativo
if __name__ == "__main__":
    main()
