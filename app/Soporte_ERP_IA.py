import streamlit as st

# Configuración de página con tu nombre profesional
st.set_page_config(page_title="Nexus ERP - Gaston Di Campli", layout="wide", page_icon="🚀")

# Estilo para el Copyright fijo y profesional al final
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
    z-index: 100;
}
</style>
<div class="footer">
    <p>© 2026 | Desarrollado por Gaston Di Campli | Nexus ERP AI Suite</p>
</div>
"""
st.markdown(footer, unsafe_allow_html=True)

st.title("🚀 Nexus ERP: Automatización de Soporte con GenAI")
st.markdown("---")

# --- SECCIÓN DE INSTRUCCIONES PARA RECLUTADORES ---
st.header("🔍 Guía de Demo para Reclutadores")
st.info("""
**Siga este flujo para evaluar la integración técnica:**
1. **Disparo del Workflow:** Envíe un correo a `erpsoporteia@gmail.com` detallando un problema técnico ficticio.
2. **Respuesta Inteligente:** Recibirá un email en segundos con un **Ticket ID** y un análisis redactado por **Google Gemini**.
3. **Validación de Usuario:** Use su ID en el **Portal de Clientes** para seguir el historial.
4. **Gestión de Agente:** Ingrese al **Dashboard** para ver el análisis de sentimiento y actualizar el estado del ticket.
""")

st.markdown("### Seleccione su perfil para ingresar:")
col1, col2 = st.columns(2)

with col1:
    st.subheader("👤 Portal de Clientes")
    st.write("Interfaz de cara al usuario para consulta de estados y trazabilidad.")
    # Link real del Portal de Clientes
    st.link_button("Ir al Portal de Clientes", "https://portclientes.streamlit.app/")

with col2:
    st.subheader("🛠️ Dashboard de Agentes")
    st.write("Panel administrativo con IA Insights y gestión de base de datos Supabase.")
    # Link real del Dashboard de Agentes
    st.link_button("Ir al Dashboard de Agentes", "https://dashboardagente.streamlit.app/")

st.markdown("---")
st.markdown("#### Stack Tecnológico del Proyecto:")
st.code("Python (Streamlit) | n8n (Automation) | Google Gemini (GenAI) | Supabase (PostgreSQL) | Railway (Cloud)")