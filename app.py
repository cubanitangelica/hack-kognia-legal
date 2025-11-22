import streamlit as st
import os
import tempfile
import google.generativeai as genai
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.llms.gemini import Gemini
from llama_index.embeddings.gemini import GeminiEmbedding

st.set_page_config(page_title="Hack-Kognia Fix", layout="wide")
st.title("🛠️ Asistente Legal - Versión Estable")

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("Configuración")
    api_key = st.text_input("Pega tu API Key", type="password")
    
    # Menú simple para elegir modelo
    model_option = st.selectbox(
        "Modelo de IA:",
        ["models/gemini-1.5-flash", "models/gemini-pro"]
    )

if api_key:
    # 1. Configuración Básica
    os.environ["GOOGLE_API_KEY"] = api_key.strip()
    
    # 2. Prueba de conexión rápida
    try:
        genai.configure(api_key=api_key.strip())
        st.success("✅ Conexión con Google establecida.")
        
        # Configurar LlamaIndex con el modelo elegido
        Settings.llm = Gemini(model=model_option)
        Settings.embed_model = GeminiEmbedding(model_name="models/embedding-001")
        
    except Exception as e:
        st.error(f"Error de conexión: {e}")

    # 3. Sistema de Archivos (RAG)
    st.divider()
    uploaded_file = st.file_uploader("Sube el PDF legal aquí", type=['pdf'])
    
    if uploaded_file:
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = os.path.join(temp_dir, "temp.pdf")
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getvalue())
                
                with st.spinner("Procesando documento..."):
                    # Cargar
                    documents = SimpleDirectoryReader(input_dir=temp_dir).load_data()
                    # Indexar
                    index = VectorStoreIndex.from_documents(documents)
                    query_engine = index.as_query_engine()
                    st.success("✅ Documento listo para preguntas.")
                    
                    # Chat simple
                    prompt = st.text_input("¿Qué quieres saber del documento?")
                    if prompt:
                        response = query_engine.query(prompt)
                        st.write(response.response)
                        
                        with st.expander("Ver evidencia en el texto"):
                            if hasattr(response, 'source_nodes') and response.source_nodes:
                                st.info(response.source_nodes[0].get_content())
                            else:
                                st.warning("Respuesta general (sin cita específica).")
                                
        except Exception as e:
            st.error(f"Ocurrió un error técnico: {e}")

elif not api_key:
    st.info("👈 Pega tu API Key en la izquierda para empezar.")
    st.info("👈 Pega la llave para iniciar el diagnóstico.")
