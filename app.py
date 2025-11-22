import streamlit as st
import os
import tempfile
import google.generativeai as genai
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.llms.gemini import Gemini
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

st.set_page_config(page_title="Hack-Kognia Final", layout="wide")
st.title("⚖️ Asistente Legal - Versión Blindada")

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("Configuración")
    api_key = st.text_input("Pega tu Google API Key", type="password")
    st.success("Sistema usando: Gemini 1.5 Flash + Embeddings Locales")

if api_key:
    # 1. Configuración de la Clave
    os.environ["GOOGLE_API_KEY"] = api_key.strip()
    
    try:
        # --- CONFIGURACIÓN SEGURA (El cambio clave) ---
        
        # A. CEREBRO: Usamos Gemini 1.5 Flash (El más nuevo y compatible)
        Settings.llm = Gemini(model="models/gemini-1.5-flash", temperature=0)
        
        # B. MEMORIA: Usamos Embeddings LOCALES (HuggingFace)
        # Esto elimina el error de OpenAI y el error 404 de Google Embeddings
        Settings.embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
        
        st.sidebar.success("✅ Configuración cargada correctamente")
        
        # --- SISTEMA DE ARCHIVOS ---
        uploaded_file = st.file_uploader("Sube el PDF legal aquí", type=['pdf'])
        
        if uploaded_file:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = os.path.join(temp_dir, "temp.pdf")
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getvalue())
                
                with st.spinner("Procesando documento localmente... (Esto no falla)"):
                    try:
                        # Cargar
                        documents = SimpleDirectoryReader(input_dir=temp_dir).load_data()
                        # Indexar (Ahora se hace en el servidor, sin API externa)
                        index = VectorStoreIndex.from_documents(documents)
                        query_engine = index.as_query_engine()
                        st.success("✅ ¡Documento listo! Pregunta abajo.")
                        
                        # --- CHAT ---
                        st.divider()
                        
                        # Historial
                        if "messages" not in st.session_state:
                            st.session_state.messages = []

                        for message in st.session_state.messages:
                            with st.chat_message(message["role"]):
                                st.markdown(message["content"])

                        # Input
                        if prompt := st.chat_input("Ej: ¿De qué trata este documento?"):
                            st.session_state.messages.append({"role": "user", "content": prompt})
                            with st.chat_message("user"):
                                st.markdown(prompt)

                            with st.chat_message("assistant"):
                                with st.spinner("Analizando..."):
                                    response = query_engine.query(prompt)
                                    st.markdown(response.response)
                                    
                                    # Evidencia
                                    with st.expander("Ver fragmento del texto (Evidencia)"):
                                        if hasattr(response, 'source_nodes') and response.source_nodes:
                                            st.info(response.source_nodes[0].get_content())
                                    
                                    st.session_state.messages.append({"role": "assistant", "content": response.response})
                                    
                    except Exception as e:
                        st.error(f"Error procesando el archivo: {e}")

    except Exception as e:
        st.error(f"Error de configuración general: {e}")

elif not api_key:
    st.info("👈 Pega tu llave para empezar.")
