import streamlit as st
import os
import tempfile
import google.generativeai as genai
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from gtts import gTTS
import io

# --- CONFIGURACIÓN VISUAL PRO ---
st.set_page_config(page_title="Kognia Legal AI", layout="wide", page_icon="⚖️")

# CSS para estilo profesional
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        height: 3em;
    }
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">⚖️ Kognia: Justicia Accesible</h1>', unsafe_allow_html=True)

# --- BARRA LATERAL (CON EL DETECTOR AUTOMÁTICO DE VUELTA) ---
with st.sidebar:
    st.header("⚙️ Configuración")
    api_key = st.text_input("🔑 Google API Key", type="password")
    
    model_choice = None
    
    # --- AQUÍ ESTÁ LA MAGIA QUE RECUPERAMOS ---
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key.strip()
        genai.configure(api_key=api_key.strip())
        
        try:
            with st.spinner("Conectando con Google..."):
                # Preguntamos a Google qué modelos tiene tu llave
                modelos_disponibles = []
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods:
                        modelos_disponibles.append(m.name)
                
                # Filtramos para que solo salgan los Gemini
                mejores_modelos = [m for m in modelos_disponibles if "gemini" in m and "vision" not in m]
                
                if not mejores_modelos:
                    mejores_modelos = ["models/gemini-1.5-flash"] # Por si acaso
                    
                st.success(f"✅ ¡Conectado! {len(mejores_modelos)} modelos detectados.")
                model_choice = st.selectbox("🧠 Selecciona tu modelo:", mejores_modelos)
                
        except Exception as e:
            st.error("Error validando la llave.")
    
    st.markdown("---")
    st.caption("Hack-Kognia 2025")

# --- FUNCIÓN DE AUDIO ---
def texto_a_audio(texto):
    try:
        tts = gTTS(text=texto, lang='es')
        audio_bytes = io.BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        return audio_bytes
    except Exception:
        return None

# --- LÓGICA PRINCIPAL ---
if api_key and model_choice:
    
    # Configuración Embeddings Locales
    try:
        Settings.embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
        Settings.llm = None 
    except Exception:
        pass

    # PESTAÑAS
    tab1, tab2 = st.tabs(["💬 Chat con el Documento", "🆚 Traductor Jurídico"])

    # --- PESTAÑA 1: CHAT RAG ---
    with tab1:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.info("📂 **Carga de Documento**")
            uploaded_file = st.file_uploader("Sube PDF (Leyes, Contratos)", type=['pdf'])

        # Indexación
        retriever = None
        if uploaded_file:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = os.path.join(temp_dir, "temp.pdf")
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getvalue())
                
                with st.spinner("🧠 Indexando documento..."):
                    try:
                        documents = SimpleDirectoryReader(input_dir=temp_dir).load_data()
                        index = VectorStoreIndex.from_documents(documents)
                        retriever = index.as_retriever(similarity_top_k=5)
                    except Exception:
                        pass # Silencioso si falla la lectura inicial

        with col2:
            if uploaded_file and retriever:
                st.success("✅ Documento listo. Pregunta:")
                
                if "messages" not in st.session_state:
                    st.session_state.messages = []

                for message in st.session_state.messages:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])

                if prompt := st.chat_input("Ej: ¿Qué dice sobre las multas?"):
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    with st.chat_message("user"):
                        st.markdown(prompt)

                    with st.chat_message("assistant"):
                        with st.spinner("Pensando..."):
                            try:
                                # RAG
                                nodes = retriever.retrieve(prompt)
                                contexto = "\n\n".join([n.get_content() for n in nodes])
                                
                                full_prompt = f"""
                                Eres un asistente legal claro y útil.
                                Contexto del PDF: {contexto}
                                Pregunta: {prompt}
                                Responde basándote solo en el contexto.
                                """
                                
                                model = genai.GenerativeModel(model_choice)
                                response = model.generate_content(full_prompt)
                                
                                st.markdown(response.text)
                                
                                # AUDIO AUTO-GENERADO
                                audio = texto_a_audio(response.text)
                                if audio:
                                    st.audio(audio, format='audio/mp3')
                                
                                with st.expander("🔍 Ver Evidencia"):
                                    st.caption(contexto)
                                    
                                st.session_state.messages.append({"role": "assistant", "content": response.text})
                            except Exception as e:
                                st.error(f"Error: {e}")

    # --- PESTAÑA 2: TRADUCTOR ---
    with tab2:
        st.header("Traductor de Lenguaje Claro")
        texto_complejo = st.text_area("Pega un texto difícil aquí:", height=150)
        
        if st.button("Traducir y Explicar"):
            with st.spinner("Traduciendo..."):
                prompt_trad = f"Explica esto como para un niño de 10 años en una tabla comparativa: {texto_complejo}"
                model = genai.GenerativeModel(model_choice)
                res = model.generate_content(prompt_trad)
                st.markdown(res.text)
                
                audio_trad = texto_a_audio(res.text.replace("|", " "))
                if audio_trad:
                    st.audio(audio_trad, format='audio/mp3')

elif not api_key:
    st.warning("👈 Pega tu API Key para que el sistema detecte tus modelos.")
