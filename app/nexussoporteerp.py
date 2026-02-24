import streamlit as st

st.set_page_config(page_title="Nexus ERP - Centro de Pruebas", page_icon="🚀")

st.title("🚀 Nexus ERP Support - Centro de Pruebas")
st.markdown("""
Bienvenido al ecosistema de soporte inteligente. Sigue esta guía para probar la integración completa:
""")

col1, col2 = st.columns(2)

with col1:
    st.info("### 1. El Disparador (Email)")
    st.write("Envía un correo para generar un ticket automáticamente.")
    st.code("Para: erpsoporteia@gmail.com\nAsunto: Error en Facturación TK-Test\nCuerpo: No puedo emitir facturas A.")
    st.success("🤖 **¿Qué pasará?** n8n procesará el correo, Gemini creará una respuesta inteligente y el ticket aparecerá en el Dashboard.")

with col2:
    st.warning("### 2. Gestión (Dashboard)")
    st.write("Entra como Agente o Admin para gestionar el caso.")
    st.link_button("Ir al Dashboard Admin", "https://tu-url-dashboard.streamlit.app")
    st.caption("Usa el botón 'Modo Demo' en la barra lateral.")

st.divider()

col3, col4 = st.columns(2)

with col3:
    st.success("### 3. Seguimiento (Portal)")
    st.write("Mira cómo el cliente ve su ticket y las respuestas de la IA.")
    st.link_button("Ir al Portal Cliente", "https://tu-url-portal.streamlit.app")

with col4:
    st.image("https://cdn-icons-png.flaticon.com/512/8943/8943377.png", width=100)
    st.write("**Tecnologías:** n8n, Supabase, Gemini AI, Streamlit.")