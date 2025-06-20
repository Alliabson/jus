import streamlit as st
import google.generativeai as genai
from utils.document_parser import parse_legal_document
from utils.calculations import calculate_legal_dates
from services.defense_strategy import generate_defense
from services.accusation_strategy import generate_accusation
from utils.legal_api import fetch_jurisprudence

# Configuração
genai.configure(api_key="AIzaSyCVuV01e2Klwf8qHgZXBTZrWkGt1qJ0Q0o")
model = genai.GenerativeModel('gemini-pro')

st.set_page_config(page_title="Assistente Jurídico IA", layout="wide")

def main():
    st.title("🤖 Assistente Jurídico Inteligente")
    
    with st.sidebar:
        st.header("Configurações")
        area_juridica = st.selectbox("Área Jurídica", ["Civil", "Criminal", "Previdenciário"])
        tipo_acao = st.radio("Tipo de Ação", ["Defesa", "Acusação"])
    
    tab1, tab2, tab3 = st.tabs(["Análise", "Estratégia", "Legislação"])
    
    with tab1:
        uploaded_file = st.file_uploader("Carregue a peça jurídica", type=["pdf", "docx"])
        if uploaded_file:
            document_text = parse_legal_document(uploaded_file)
            st.session_state.document_text = document_text
            st.success("Documento processado com sucesso!")
            
            with st.expander("Visualizar texto extraído"):
                st.text(document_text[:5000] + "...")
    
    with tab2:
        if 'document_text' in st.session_state:
            if tipo_acao == "Defesa":
                strategy = generate_defense(document_text, area_juridica)
            else:
                strategy = generate_accusation(document_text, area_juridica)
            
            st.subheader("Estratégia Jurídica Recomendada")
            st.write(strategy)
    
    with tab3:
        search_term = st.text_input("Buscar jurisprudência")
        if search_term:
            results = fetch_jurisprudence(search_term, area_juridica)
            st.json(results)

if __name__ == "__main__":
    main()
