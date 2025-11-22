import streamlit as st
import os
import tempfile
import google.generativeai as genai
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.llms.gemini import Gemini
from llama_index.embeddings.gemini import GeminiEmbedding

st.set_page_config(page_title="Hack-Kognia Fix", layout="wide")
st.title("🛠️ Modo de Recuperación: Hack-Kognia")

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("Configuración")
    api_key = st.text_input("Pega tu NUEVA API Key", type="password")
    
    # Selector de modelo manual sin prefijos raros
    model_name = st.selectbox(
        "Selecciona modelo:",
        ["gemini-1.5-flash", "gemini-pro", "gemini-1.5-pro-latest"]
    )

if api_key:
    os.environ["GOOGLE_API_KEY"] = api_key.strip()
    
    # --- PRUEBA 1: CONEXIÓN DIRECTA (Sin LlamaIndex) ---
    st.subheader("Paso 1: Prueba de Conexión Directa")
    try:
        genai.configure(api_key=api_key.strip())
        # Probamos listar modelos para ver si la llave funciona
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Di 'Hola Hackathon' si me escuchas.")
        st.success(f"✅ CONEXIÓN EXITOSA: Google respondió: {response.text}")
        connection_success = True
    except Exception as e:
        st.error(f"❌ LA LLAVE FALLÓ: {e}")
        st.warning("Solución: Tu API Key no sirve o no tiene permisos. Crea una nueva en aistudio.google.com")
        connection_success = False

    # --- PRUEBA 2: INTENTO DE RAG (Solo si la 1 funciona) ---
    if connection_success:
        st.divider()
        st.subheader("Paso 2: Sistema RAG (Documentos)")
        
        uploaded_file = st.file_uploader("Sube el PDF ahora", type=['pdf'])
        
        if uploaded_file:
            try:
                # Configuración explícita para LlamaIndex
                # Nota: A veces el embedding falla si no se especifica el modelo exacto
                Settings.llm = Gemini(model=f"models/{model_name}")
                Settings.embed_model = GeminiEmbedding(model_name="models/embedding-001")
                
                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_path = os.path.join(temp_dir, "temp.pdf")
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getvalue())
                    
                    with st.spinner("Creando Embeddings..."):
                        documents = SimpleDirectoryReader(input_dir=temp_dir).load_data()
                        index = VectorStoreIndex.from_documents(documents)
                        query_engine = index.as_query_engine()
                        st.success("✅ Indexación RAG Exitosa")
                        
                        prompt = st.text_input("Pregunta al PDF:")
                        if prompt:
                            resp = query_engine.query(prompt)
                            st.write(resp.response)
                            with st.expander("Ver fuente"):
                                st.write(resp.source_nodes[0].get_content())
                                
            except Exception as e:
                st.error(f"❌ Error en RAG: {e}")
                st.info("Intenta cambiar el modelo en el menú de la izquierda.")

elif not api_key:
    st.info("👈 Pega la llave para iniciar el diagnóstico.")
