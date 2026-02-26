import streamlit as st

st.set_page_config(page_title="Nexus ERP AI - Experience Center", layout="wide")

st.title("🚀 Nexus ERP: AI Support Suite")
st.markdown("""
Bienvenido a la demo interactiva de **Nexus ERP**. 
Este sistema utiliza una arquitectura basada en **n8n, Google Gemini y Supabase** para automatizar el soporte técnico.
""")

col1, col2 = st.columns(2)

with col1:
    st.header("👤 Portal de Clientes")
    st.info("Simula ser un cliente que necesita ayuda.")
    st.markdown("""
    **Instrucciones de Demo:**
    1. Envía un mail a `erpsoporteia@gmail.com`.
    2. Recibirás un **Ticket ID**.
    3. Ingresa el ID aquí para ver el seguimiento.
    """)
    if st.button("Ir al Portal de Clientes"):
        # Aquí rediriges a la URL de tu app de clientes
        st.write("Redirigiendo a: `url-de-tu-app-cliente.streamlit.app`")

with col2:
    st.header("🛠️ Dashboard de Agentes")
    st.warning("Acceso exclusivo para personal de soporte (Reclutadores).")
    st.markdown("""
    **Instrucciones de Demo:**
    - Observa cómo la IA ya categorizó el ticket que enviaste.
    - Mira el análisis de sentimiento y la prioridad automática.
    - Gestiona el estado del ticket desde el panel.
    """)
    if st.button("Ir al Dashboard de Agentes"):
        # Aquí rediriges a la URL de tu dashboard de gestión
        st.write("Redirigiendo a: `url-de-tu-dashboard-agente.streamlit.app`")

st.divider()
st.caption("Desarrollado por [Tu Nombre] - Stack: Python, Streamlit, n8n, Supabase, Google Gemini AI.")