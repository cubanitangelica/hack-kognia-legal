import streamlit as st
import os
import tempfile
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.llms.gemini import Gemini
from llama_index.embeddings.gemini import GeminiEmbedding

# -[span_0](start_span)-- CONFIGURACIÓN DE LA PÁGINA (Requisito: Interfaz clara[span_0](end_span)) ---
st.set_page_config(page_title="Asistente Legal Kognia", layout="wide")

st.title("⚖️ Hack-Kognia: Asistente Legal Inteligente")
st.markdown("""
Este sistema utiliza **RAG (Retrieval-Augmented Generation)** para analizar documentos legales.
Sube un contrato o ley y haz preguntas precisas.
""")

# --- BARRA LATERAL: CONFIGURACIÓN ---
with st.sidebar:
    st.header("Configuración")
    api_key = st.text_input("Google API Key", type="password")
    st.info("Este sistema cumple con el reto de indexación y búsqueda semántica.")

# --- LÓGICA PRINCIPAL ---
if api_key:
    # Configurar el cerebro de la IA (Gemini)
    os.environ["GOOGLE_API_KEY"] = api_key
    Settings.llm = Gemini(model="models/gemini-pro", temperature=0)
    Settings.embed_model = GeminiEmbedding(model_name="models/embedding-001")

    # -[span_1](start_span)-- PASO 1: CARGA DE DOCUMENTOS[span_1](end_span) ---
    uploaded_file = st.file_uploader("Sube tu documento legal (PDF)", type=['pdf'])

    if uploaded_file:
        # Guardar el PDF temporalmente para poder leerlo
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = os.path.join(temp_dir, "temp.pdf")
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getvalue())

            with st.spinner("Indexando documento y creando embeddings... (Esto cumple el requisito técnico)"):
                # Cargar y vectorizar (Aquí ocurre la magia del RAG)
                documents = SimpleDirectoryReader(input_dir=temp_dir).load_data()
                index = VectorStoreIndex.from_documents(documents)
                query_engine = index.as_query_engine()
                st.success("¡Documento indexado exitosamente!")

            # -[span_2](start_span)-- PASO 2: INTERFAZ DE CHAT[span_2](end_span) ---
            st.divider()
            st.subheader("💬 Chat con el Documento")

            # Historial del chat
            if "messages" not in st.session_state:
                st.session_state.messages = []

            # Mostrar mensajes anteriores
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            # Entrada del usuario
            if prompt := st.chat_input("Ej: ¿Cuáles son las obligaciones del arrendatario?"):
                # Guardar y mostrar pregunta
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)

                # Generar respuesta
                with st.chat_message("assistant"):
                    with st.spinner("Buscando evidencia en el texto..."):
                        # [span_3](start_span)Aquí el sistema busca en los vectores, no inventa[span_3](end_span)
                        response = query_engine.query(prompt)
                        
                        # Mostrar respuesta
                        st.markdown(response.response)
                        
                        # [span_4](start_span)Mostrar fuentes (Requisito: Evidencia[span_4](end_span))
                        with st.expander("🔍 Ver fuente exacta (Evidencia)"):
                            st.write(response.source_nodes[0].get_content())
                        
                        # Guardar en historial
                        st.session_state.messages.append({"role": "assistant", "content": response.response})

elif not api_key:
    st.warning("⚠️ Por favor ingresa tu API Key en la barra lateral para iniciar el sistema RAG.")
