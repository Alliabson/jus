import streamlit as st
import google.generativeai as genai
import sys
from pathlib import Path
import traceback
import os # Importar para usar os.getenv
from dotenv import load_dotenv # Importar para carregar .env localmente

# Configura caminhos
sys.path.append(str(Path(__file__).parent))

try:
    from utils.document_parser import parse_legal_document
    from utils.legal_api import fetch_jurisprudence
    from services.defense_strategy import generate_defense
    from services.accusation_strategy import generate_accusation
except ImportError as e:
    st.error(f"Erro de importação de módulo: {str(e)}")
    st.info("Verifique se os arquivos nas pastas 'utils' e 'services' existem e se seus nomes estão corretos.")
    st.stop()

# --- BLOCÔNICO DE CONFIGURAÇÃO DA CHAVE DE API (Corrigido Definitivamente) ---
API_KEY = None
try:
    # Tenta carregar a chave do Streamlit Secrets (ideal para Streamlit Cloud)
    # AQUI ACESSAMOS PELO NOME DA VARIÁVEL/SEGREDO: "GOOGLE_API_KEY"
    API_KEY = st.secrets["GOOGLE_API_KEY"]
except KeyError:
    # Se não estiver em st.secrets, tenta carregar do arquivo .env (para execução local)
    load_dotenv() # Carrega as variáveis do arquivo .env
    # AQUI TAMBÉM ACESSAMOS PELO NOME DA VARIÁVEL: "GOOGLE_API_KEY"
    API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    st.error("Erro crítico: A chave da API do Google Gemini não foi encontrada.")
    st.error("Por favor, configure-a corretamente:")
    # A MENSAGEM DE ERRO TAMBÉM DEVE USAR O NOME DA VARIÁVEL, NÃO O VALOR DA SUA CHAVE.
    st.error("- **No Streamlit Cloud:** Vá em 'Manage app' -> 'Secrets' e adicione `GOOGLE_API_KEY=\"SUA_CHAVE_AQUI\"`")
    st.error("- **Localmente:** Crie um arquivo `.env` na raiz do seu projeto com `GOOGLE_API_KEY=\"SUA_CHAVE_AQUI\"`")
    st.stop() # Interrompe a execução do Streamlit se a chave não for encontrada

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')
# --- FIM DO BLOCÔNICO DE CONFIGURAÇÃO ---


def main():
    st.set_page_config(page_title="Assistente Jurídico IA", layout="wide")

    st.title("🤖 Assistente Jurídico Inteligente")

    with st.sidebar:
        st.header("Configurações")
        area_juridica = st.selectbox("Área Jurídica", ["Civil", "Criminal", "Previdenciário", "Outra"]) # Adicionei "Outra"
        tipo_acao = st.radio("Tipo de Ação", ["Defesa", "Acusação"])
        # Adicionei um input para refinar a estratégia, útil para a IA
        contexto_estrategia = st.text_area(
            "Contexto ou Ponto Principal da Estratégia (opcional):",
            "Ex: 'foco na ausência de provas', 'alegar cerceamento de defesa'"
        )

    tab1, tab2, tab3 = st.tabs(["Análise e Upload", "Estratégia e Argumentos", "Legislação e Jurisprudência"]) # Renomeei as abas

    with tab1:
        st.subheader("1. Carregue e Analise a Peça Jurídica")
        uploaded_file = st.file_uploader("Carregue a peça jurídica", type=["pdf", "docx"])
        document_text = st.text_area("Ou cole o texto da peça jurídica aqui (se preferir ou para testes rápidos):", height=300)

        if uploaded_file:
            try:
                # Prioriza o upload de arquivo se houver
                text_from_file = parse_legal_document(uploaded_file)
                st.session_state.document_text = text_from_file
                st.success("Documento processado do arquivo com sucesso!")
                with st.expander("Visualizar texto extraído do arquivo"):
                    st.text(text_from_file[:5000] + ("..." if len(text_from_file) > 5000 else "")) # Limita exibição
            except Exception as e:
                st.error(f"Erro ao processar documento carregado: {str(e)}")
                st.info("Certifique-se de que o arquivo PDF/DOCX está bem formatado e não está corrompido.")
                st.exception(e) # Exibe o traceback completo para depuração
        elif document_text: # Se não houver upload, usa o texto colado
            st.session_state.document_text = document_text
            st.success("Texto colado processado com sucesso!")
            with st.expander("Visualizar texto colado"):
                st.text(document_text[:5000] + ("..." if len(document_text) > 5000 else ""))

        if 'document_text' in st.session_state and st.session_state.document_text:
            st.markdown("---")
            st.subheader("Análise Preliminar do Documento (IA)")
            if st.button("Analisar Texto com IA"):
                with st.spinner("A IA está analisando o texto..."):
                    try:
                        prompt_analise = f"""
                        Analise o seguinte texto jurídico. Identifique as seguintes informações:
                        1. Um breve resumo do conteúdo (máximo 5 frases).
                        2. O(s) ramo(s) do direito mais provável(is) (Ex: Civil, Criminal, Previdenciário, Administrativo, etc.).
                        3. Os 5-7 pontos mais importantes ou palavras-chave relevantes (entidades, conceitos-chave).
                        4. As partes envolvidas (Requerente/Autor, Requerido/Réu, etc.).
                        5. O objetivo principal da peça (Ex: Cobrança, Defesa, Recurso, etc.).

                        Formate a resposta de forma clara e com tópicos:
                        **Resumo:** [Seu resumo aqui]
                        **Ramo(s) do Direito:** [Ramo1, Ramo2]
                        **Pontos Chave:** [ponto1, ponto2, ponto3, ...]
                        **Partes Envolvidas:** [Parte A: Nome, Parte B: Nome]
                        **Objetivo da Peça:** [Objetivo]

                        Texto para análise:
                        {st.session_state.document_text}
                        """
                        response = model.generate_content(prompt_analise)
                        st.markdown(response.text) # Use markdown para formatar a resposta da IA

                    except Exception as e:
                        st.error(f"Erro ao gerar análise da IA: {str(e)}")
                        st.info("Verifique se o texto é legível e se há conectividade com a API do Gemini.")
                        st.exception(e)

    with tab2:
        st.subheader("2. Geração de Estratégia e Argumentos")
        if 'document_text' not in st.session_state or not st.session_state.document_text:
            st.warning("Por favor, carregue ou cole um documento na aba 'Análise' primeiro.")
        else:
            st.info(f"Gerando estratégia para **{tipo_acao}** na área **{area_juridica}**.")
            st.write("Considerando o texto da peça jurídica e o contexto fornecido.")

            if st.button(f"Gerar Estratégia de {tipo_acao}"):
                with st.spinner(f"A IA está formulando a estratégia de {tipo_acao}..."):
                    try:
                        if tipo_acao == "Defesa":
                            strategy = generate_defense(st.session_state.document_text, area_juridica, contexto_estrategia, model)
                        else: # Acusação
                            strategy = generate_accusation(st.session_state.document_text, area_juridica, contexto_estrategia, model)

                        st.subheader(f"Estratégia de {tipo_acao} Recomendada pela IA:")
                        st.markdown(strategy) # Use markdown para formatar a resposta da IA

                    except Exception as e:
                        st.error(f"Erro ao gerar estratégia de {tipo_acao}: {str(e)}")
                        st.info("Verifique a qualidade do texto e do prompt. Tente novamente.")
                        st.exception(e)

    with tab3:
        st.subheader("3. Busca de Legislação e Jurisprudência")
        search_term_legis = st.text_input("Buscar Legislação (ex: 'Lei 8.213/91', 'Código Civil Art. 421')", key="legis_search")
        if st.button("Buscar Legislação (Exemplo)", key="btn_legis_search"):
            if search_term_legis:
                # Aqui você chamaria uma função específica para buscar legislação,
                # talvez usando a API do Senado Federal ou um web scraper.
                # Por enquanto, vamos simular com o Gemini.
                with st.spinner(f"Buscando legislação para '{search_term_legis}'..."):
                    try:
                        legis_prompt = f"""
                        Com base na legislação brasileira, forneça informações sobre: {search_term_legis}.
                        Inclua o número da lei, artigo(s) relevante(s) e um breve resumo.
                        Se não for uma lei específica, forneça conceitos gerais relacionados ao termo.
                        """
                        response_legis = model.generate_content(legis_prompt)
                        st.subheader("Legislação Encontrada (Via IA):")
                        st.markdown(response_legis.text)
                    except Exception as e:
                        st.error(f"Erro ao buscar legislação com IA: {str(e)}")
                        st.exception(e)
            else:
                st.warning("Por favor, digite um termo para buscar legislação.")


        st.markdown("---")
        search_term_juris = st.text_input("Buscar Jurisprudência (ex: 'danos morais', 'responsabilidade civil')", key="juris_search")
        if st.button("Buscar Jurisprudência Externa", key="btn_juris_search"):
            if search_term_juris:
                with st.spinner(f"Buscando jurisprudência para '{search_term_juris}' na área '{area_juridica}'..."):
                    try:
                        # Chama a função do seu utils/legal_api.py
                        results = fetch_jurisprudence(search_term_juris, area_juridica)
                        if results and not results.get("error"):
                            st.subheader(f"Resultados da Jurisprudência para: '{results['termo']}'")
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

# Disclaimer final
st.markdown("---")
st.caption("⚠️ **Atenção:** Este aplicativo utiliza inteligência artificial e serve apenas como uma ferramenta de **assistência**. As informações geradas não constituem aconselhamento jurídico e devem ser sempre revisadas e validadas por um profissional do direito qualificado.")
st.caption("A busca de jurisprudência externa é uma simulação. Para uso real, configure a URL e os parâmetros de uma API jurídica pública (ex: TJDFT, CNJ DataJud) ou paga.")

if __name__ == "__main__":
    main()
