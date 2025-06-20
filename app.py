import streamlit as st
import google.generativeai as genai
import sys
from pathlib import Path
import traceback

# Configura caminhos
sys.path.append(str(Path(__file__).parent))

try:
    from utils.document_parser import parse_legal_document
    from utils.legal_api import fetch_jurisprudence
    from services.defense_strategy import generate_defense
    from services.accusation_strategy import generate_accusation
except ImportError as e:
    st.error(f"Erro de importação: {str(e)}")
    st.stop()

# Configuração do Gemini
genai.configure(api_key=st.secrets["AIzaSyCVuV01e2Klwf8qHgZXBTZrWkGt1qJ0Q0o"])
model = genai.GenerativeModel('gemini-pro')

def main():
    st.set_page_config(page_title="Assistente Jurídico IA", layout="wide")
    
    st.title("🤖 Assistente Jurídico Inteligente")
    
    with st.sidebar:
        st.header("Configurações")
        area_juridica = st.selectbox("Área Jurídica", ["Civil", "Criminal", "Previdenciário"])
        tipo_acao = st.radio("Tipo de Ação", ["Defesa", "Acusação"])
    
    tab1, tab2, tab3 = st.tabs(["Análise", "Estratégia", "Legislação"])
    
    with tab1:
        uploaded_file = st.file_uploader("Carregue a peça jurídica", type=["pdf", "docx"])
        if uploaded_file:
            try:
                document_text = parse_legal_document(uploaded_file)
                st.session_state.document_text = document_text
                st.success("Documento processado com sucesso!")
                with st.expander("Visualizar texto extraído"):
                    st.text(document_text[:5000] + "...")
            except Exception as e:
                st.error(f"Erro ao processar documento: {str(e)}")
    
    with tab2:
        if 'document_text' in st.session_state:
            try:
                if tipo_acao == "Defesa":
                    strategy = generate_defense(st.session_state.document_text, area_juridica, model)
                else:
                    strategy = generate_accusation(st.session_state.document_text, area_juridica, model)
                
                st.subheader("Estratégia Jurídica Recomendada")
                st.write(strategy)
            except Exception as e:
                st.error(f"Erro ao gerar estratégia: {str(e)}")
    
    with tab3:
        search_term = st.text_input("Buscar jurisprudência (ex: 'danos morais')")
        if search_term:
            try:
                results = fetch_jurisprudence(search_term, area_juridica)
                st.json(results)
            except Exception as e:
                st.error(f"Erro na busca: {str(e)}")

if __name__ == "__main__":
    main()
