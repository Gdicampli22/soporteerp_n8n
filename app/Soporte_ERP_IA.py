import streamlit as st

# Configuración de página profesional con tu nombre Gaston Di Campli
st.set_page_config(page_title="Nexus ERP - Gaston Di Campli", layout="wide", page_icon="🚀")

# Estilo UX Profesional: Paleta LinkedIn con tipografía clara
st.markdown("""
<style>
    /* Fondo y tipografía base de Streamlit para limpieza */
    .stApp {
        background-color: #ffffff;
        color: #333333;
    }
    
    /* Botones estilo LinkedIn: Azul Profundo con texto claro */
    .demo-button {
        display: inline-block;
        padding: 10px 20px;
        color: #ffffff !important; /* Texto claro */
        background-color: #004182; /* Azul LinkedIn */
        border-radius: 5px;
        text-decoration: none;
        font-weight: bold;
        text-align: center;
        transition: background-color 0.3s;
        border: none;
        font-size: 16px;
    }
    .demo-button:hover {
        background-color: #0077b5; /* Azul más claro al hover */
    }
    
    /* Footer Profesional Gaston Di Campli */
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #0e1117; /* Fondo oscuro profesional */
        color: #fafafa; /* Texto claro */
        text-align: center;
        padding: 10px;
        font-size: 14px;
        border-top: 1px solid #333;
        z-index: 100;
    }
    
    /* Títulos claros */
    h1, h2, h3 {
        color: #0e1117;
    }
</style>
""", unsafe_allow_html=True)

# Footer de Copyright Gaston Di Campli
st.markdown(f'<div class="footer"><p>© 2026 | Desarrollado por Gaston Di Campli | Nexus ERP AI Suite</p></div>', unsafe_allow_html=True)

# Título Principal
st.title("🚀 Nexus ERP: Automatización de Soporte con GenAI")
st.markdown("---")

# --- GUÍA PARA RECLUTADORES: Flujo claro y directo ---
st.header("🔍 Guía de Demo para Reclutadores")
st.info("""
**Siga este flujo profesional para evaluar la integración técnica de Gaston:**
1. **Inicio de Flujo:** Envíe un correo a `erpsoporteia@gmail.com` detallando un problema.
2. **Procesamiento IA:** Recibirá un email analizado por **Google Gemini** con un **Ticket ID** único.
3. **Portal Cliente:** Use su ID para validar la trazabilidad en tiempo real.
4. **Dashboard Agente:** Gestione estados y visualice el análisis de sentimiento.
""")

st.markdown("### Seleccione su perfil para ingresar:")
st.markdown("<br>", unsafe_allow_html=True) # Espaciado UX

col1, col2 = st.columns(2)

with col1:
    st.subheader("👤 Portal de Clientes")
    st.write("Interfaz limpia para seguimiento y trazabilidad de tickets por ID por parte del cliente.")
     st.write("***En el email que llega con el SLA va disponer de usuario y clave para el portal***")
    # Botón UX: Azul LinkedIn, tipografía clara, abre por fuera
    st.markdown('<a href="https://portclientes.streamlit.app/" target="_blank" class="demo-button">Ingresar como Cliente</a>', unsafe_allow_html=True)

with col2:
    st.subheader("🛠️ Dashboard de Agentes")
    st.write("Panel administrativo con IA Insights y gestión de ticket por Agentes de Soporte..")
    # Botón UX: Azul LinkedIn, tipografía clara, abre por fuera
    st.markdown('<a href="https://dashboardagente.streamlit.app/" target="_blank" class="demo-button">Ingresar como Agente</a>', unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True) # Espaciado UX
st.markdown("---")
st.markdown("#### Stack Tecnológico Profesional:")
st.code("Python (Streamlit) | n8n (Workflow) | Google Gemini AI | Supabase (DB) | Railway (Cloud)")