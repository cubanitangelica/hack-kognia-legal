# ⚖️ Kognia Legal AI — Asistente Jurídico Inteligente (RAG Híbrido)

## Resumen del Proyecto
Este proyecto es un prototipo funcional (MVP) desarrollado para el **Hackathon Caldas 2025 – Hack-Kognia 1.0**.

**Kognia Legal AI** es un asistente jurídico basado en **Inteligencia Artificial + arquitectura RAG Híbrida**, diseñado para:

- Analizar documentos legales (contratos, leyes, resoluciones).
- Realizar búsquedas semánticas dentro del documento.
- Responder preguntas con evidencia real, reduciendo alucinaciones.
- Traducir lenguaje jurídico complejo a lenguaje claro.
- Generar audio automático para accesibilidad.

La solución prioriza **privacidad**, **eficiencia** y **costo cero** en el proceso de indexación.

**DEMO EN VIVO:** [https://hack-kognia-legal-ilwv49ama8c2j7cyfhyets.streamlit.app/]

---

## Arquitectura Técnica — Enfoque RAG Híbrido

La arquitectura implementada desacopla la memoria del razonamiento, lo que permite un sistema más privado, económico y escalable.

### 1. **Memoria local (Indexación gratuita y privada)**
- Procesamiento del PDF con **LlamaIndex**.
- Embeddings locales con **HuggingFace** (`all-MiniLM-L6-v2`).
- Construcción de un índice vectorial completamente local.
- Recuperación semántica *top-k* sin usar APIs externas.

### 2. **Razonamiento (Google Gemini)**
- El modelo Gemini se usa únicamente para redactar la respuesta final.
- Recibe solo el contexto recuperado del PDF.
- Se optimiza costo, velocidad y se evitan alucinaciones.

### 3. **Accesibilidad**
- Generación de audio de las respuestas usando `gTTS`.

**Ventajas del enfoque híbrido:**
- ✔ Privacidad total (el PDF nunca sale del equipo).  
- ✔ Economía (embeddings locales, no pagos innecesarios).  
- ✔ Escalabilidad.  
- ✔ Respuestas más fundamentadas.  

---

## Stack Tecnológico

**Frontend:**  
- Streamlit

**Orquestación RAG:**  
- LlamaIndex  
- HuggingFace Embeddings

**LLM:**  
- Google Generative AI — Gemini (modelo seleccionado dinámicamente)

**Accesibilidad:**  
- gTTS (audio MP3)

---

## Funcionalidades Principales

### Chat con el Documento
- Carga de PDFs legales.
- Indexación local.
- Búsqueda semántica.
- Respuestas con evidencia exacta.
- Generación de audio.

### Traductor Jurídico
- Explica textos complejos en lenguaje sencillo.
- Produce comparaciones claras.
- Audio opcional.

---

## Flujo de Arquitectura

1. Usuario ingresa su Google API Key.  
2. El sistema detecta automáticamente los modelos Gemini disponibles.  
3. Se sube un PDF.  
4. LlamaIndex extrae y segmenta el contenido.  
5. HuggingFace genera embeddings locales.  
6. Se construye un índice vectorial.  
7. El usuario hace una pregunta.  
8. Se recuperan los fragmentos más relevantes.  
9. Gemini genera una respuesta basada **exclusivamente** en el contexto.  
10. Se ofrece evidencia + audio.

---

## Pruebas Realizadas
 
- **Normativa pública:** artículos, sanciones, reglas.  
- **Traducción jurídica:** explicaciones ciudadanas.  
- **Casos sin evidencia:** el sistema reporta la ausencia correctamente.  
- **Embeddings locales:** probados sin conexión.  
- **Audio:** respuestas reproducidas con claridad.

---

## Instrucciones de Ejecución Local

1. Clonar el repositorio. 
2. Instalar dependencias:
bash
pip install -r requirements.txt
3. Configurar la API Key de Google. 
4. Ejecutar la aplicación:
bash
streamlit run app.py

## Equipo Participante del Reto Hack-Kognia 2025.
Angélica Carvajal Pulido
Dayana Andrea Henao Arbeláez 
Juan Gabriel Quiroz Gómez 
