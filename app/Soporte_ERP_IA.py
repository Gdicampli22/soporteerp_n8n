import streamlit as st

# Configuración de página
st.set_page_config(page_title="Nexus ERP - Gaston Di Campli", layout="wide")

# Estilo para el Copyright fijo al final
footer = """
<style>
.footer {
    position: fixed;
    left: 0;
    bottom: 0;
    width: 100%;
    background-color: #0e1117;
    color: #fafafa;
    text-align: center;
    padding: 10px;
    font-size: 14px;
    border-top: 1px solid #333;
}
</style>
<div class="footer">
    <p>© 2026 | Desarrollado por Gaston Di Campli | Nexus ERP AI Suite</p>
</div>
"""
st.markdown(footer, unsafe_allow_html=True)

st.title("🚀 Nexus ERP: Automatización de Soporte con GenAI")
st.markdown("---")

# --- SECCIÓN PARA RECLUTADORES ---
st.header("🔍 Guía de Demo para Reclutadores")
st.info("""
**Siga este flujo para probar la integración completa de Gaston:**
1. **Envío de Ticket:** Envíe un correo a `erpsoporteia@gmail.com` detallando un problema técnico.
2. **Respuesta IA:** Recibirá un email en segundos con un **Ticket ID** y una respuesta redactada por **Google Gemini**.
3. **Portal de Clientes:** Use su ID para ver el historial de conversación en tiempo real.
4. **Dashboard de Agentes:** Acceda para ver el análisis de sentimiento y cambiar el estado del ticket.
""")

st.markdown("### Seleccione su perfil para ingresar:")
col1, col2 = st.columns(2)

with col1:
    st.subheader("👤 Portal de Clientes")
    st.write("Interfaz para el seguimiento y consulta de tickets activos.")
    if st.button("Ingresar como Cliente"):
        st.write("Redirigiendo al portal de Gaston...")

with col2:
    st.subheader("🛠️ Dashboard de Agentes")
    st.write("Panel de control: IA Insights, prioridades y gestión de estados.")
    if st.button("Ingresar como Agente"):
        st.write("Redirigiendo al dashboard de gestión...")

st.markdown("---")
st.markdown("#### Stack Tecnológico:")
st.code("Python (Streamlit) | n8n | Google Gemini AI | Supabase | Railway Cloud")