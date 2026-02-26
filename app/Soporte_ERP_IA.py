import streamlit as st

# Configuración de página
st.set_page_config(page_title="Nexus ERP - Gaston Di Campli", layout="wide", page_icon="🚀")

# Estilo para botones HTML personalizados y Footer
st.markdown("""
<style>
    .demo-button {
        display: inline-block;
        padding: 0.5em 1em;
        color: white;
        background-color: #ff4b4b;
        border-radius: 5px;
        text-decoration: none;
        font-weight: bold;
        text-align: center;
    }
    .demo-button:hover {
        background-color: #ff3333;
        color: white;
    }
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
""", unsafe_allow_html=True)

# Footer de Copyright
st.markdown(f'<div class="footer"><p>© 2026 | Desarrollado por Gaston Di Campli | Nexus ERP AI Suite</p></div>', unsafe_allow_html=True)

st.title("🚀 Nexus ERP: Automatización de Soporte con GenAI")
st.markdown("---")

# --- GUÍA PARA RECLUTADORES ---
st.header("🔍 Guía de Demo para Reclutadores")
st.info("""
**Siga este flujo para evaluar la integración técnica:**
1. **Envío de Ticket:** Envíe un correo a `erpsoporteia@gmail.com`.
2. **Respuesta IA:** Recibirá un email (SLA) analizado por **IA** con un **Ticket ID**.
3. **Portal de Clientes:** Use su ID para seguir el historial en tiempo real.
4. **Dashboard de Agentes:** Gestione el estado y vea el análisis de sentimiento.
""")

st.markdown("### Seleccione su perfil para ingresar:")
col1, col2 = st.columns(2)

with col1:
    st.subheader("👤 Portal de Clientes")
    st.write("Seguimiento y trazabilidad de tickets.")
    # Botón HTML que fuerza la apertura en pestaña nueva
    st.markdown('<a href="https://portclientes.streamlit.app/" target="_blank" class="demo-button">Ingresar como Cliente</a>', unsafe_allow_html=True)

with col2:
    st.subheader("🛠️ Dashboard de Agentes")
    st.write("Análisis IA y gestión de estados en Supabase.")
    # Botón HTML que fuerza la apertura en pestaña nueva
    st.markdown('<a href="https://dashboardagente.streamlit.app/" target="_blank" class="demo-button">Ingresar como Agente</a>', unsafe_allow_html=True)

st.markdown("---")
st.markdown("#### Stack Tecnológico:")
st.code("Python (Streamlit) | n8n | Google Gemini AI | Supabase | Railway Cloud")