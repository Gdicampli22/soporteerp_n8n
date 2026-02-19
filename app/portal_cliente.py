import streamlit as st
from supabase import create_client, Client
import pandas as pd
import datetime
import time
import mimetypes
import plotly.express as px
import random
import re

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Nexus Portal | Autogestión",
    page_icon="🏢",
    layout="wide"
)

# --- 2. ESTILOS CSS ---
st.markdown("""
    <style>
    /* Estilo General */
    .stApp { background-color: #f8fafc; }
    
    /* Botones Azules */
    div.stButton > button {
        background-color: #1e293b !important;
        color: #ffffff !important;
        border: 1px solid #334155;
        border-radius: 8px;
        font-weight: 600;
    }
    div.stButton > button:hover {
        background-color: #3b82f6 !important;
        border-color: #3b82f6;
        color: #ffffff !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e2e8f0; }
    
    /* Insights */
    .insight-card { 
        padding: 20px; border-radius: 12px; color: white; margin-bottom: 15px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); transition: transform 0.2s;
    }
    .insight-card:hover { transform: translateY(-2px); }
    
    .card-blue { background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); }
    .card-purple { background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%); }
    .card-orange { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); }
    
    .insight-title { font-size: 0.9em; text-transform: uppercase; letter-spacing: 1px; opacity: 0.9; }
    .insight-value { font-size: 2em; font-weight: 800; margin: 5px 0; }
    .insight-desc { font-size: 0.8em; opacity: 0.8; }

    /* Chat Styling */
    .msg-container { display: flex; flex-direction: column; gap: 10px; padding: 10px; }
    .msg-box { 
        padding: 12px 16px; border-radius: 12px; font-size: 0.95em; 
        box-shadow: 0 1px 2px rgba(0,0,0,0.05); margin-bottom: 8px; max-width: 80%;
    }
    .msg-me { 
        align-self: flex-end; background-color: #eff6ff; 
        border: 1px solid #bfdbfe; color: #1e3a8a; 
        border-radius: 12px 12px 0 12px; margin-left: auto;
    }
    .msg-other { 
        align-self: flex-start; background-color: #ffffff; 
        border: 1px solid #e2e8f0; color: #334155; 
        border-radius: 12px 12px 12px 0; margin-right: auto;
    }
    .msg-meta { font-size: 0.75em; opacity: 0.7; margin-bottom: 4px; display: block; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- CONEXIÓN ---
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except:
    st.error("⚠️ Error de conexión. Verifique secrets.toml")
    st.stop()

# --- FUNCIONES ---

def mostrar_guia_demo():
    """Muestra el instructivo en la sidebar para el portafolio"""
    with st.sidebar.expander("📘 GUÍA DE LA DEMO (Leer Primero)", expanded=False):
        st.markdown("""
        **¡Bienvenido al ecosistema Nexus!**
        
        **1. 📧 El Disparador**
        * Envía un correo real al sistema (erpsoporteia@gmail.com).
        * **Asunto:** "Error crítico"
        * **Cuerpo:** "Falla el login."
        * *(n8n leerá esto y creará el ticket).*
        
        **2. 🕵️‍♂️ El Agente**
        * Entra al Dashboard.
        * Responde al ticket en el Kanban.
        
        **3. 🏢 El Cliente (Tú)**
        * Estás aquí. 
        * Ingresa como "Cliente Demo".
        * Revisa tus tickets y responde.
        """)

def registrar_auditoria(usuario, accion, detalle):
    try:
        data = { "usuario_responsable": usuario, "accion": accion, "detalle": detalle, "entidad": "Portal Cliente", "fecha": datetime.datetime.now().isoformat() }
        supabase.table("auditoria").insert(data).execute()
    except: pass

def login(email, password):
    try:
        res = supabase.table("reportantes").select("*").eq("email", email).eq("password", password).eq("activo", True).execute()
        return res.data[0] if res.data else None
    except: return None

def get_my_tickets(email):
    try:
        res = supabase.table("tickets").select("*").eq("email_reportante", email).execute()
        df = pd.DataFrame(res.data)
        if not df.empty:
            col = 'fecha_creacion' if 'fecha_creacion' in df.columns else 'created_at'
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], format='mixed', errors='coerce', utc=True)
                df = df.sort_values(by=col, ascending=False)
                df['fecha_str'] = df[col].dt.strftime('%d/%m/%Y')
        return df
    except: return pd.DataFrame()

def get_my_audit(email):
    try:
        res = supabase.table("auditoria").select("*").eq("usuario_responsable", email).order("fecha", desc=True).limit(50).execute()
        df = pd.DataFrame(res.data)
        if not df.empty:
            df['fecha'] = pd.to_datetime(df['fecha']).dt.strftime('%d/%m/%Y %H:%M')
        return df
    except: return pd.DataFrame()

def upload_file_storage(file, ticket_id):
    try:
        ts = int(time.time())
        safe_name = re.sub(r'[^a-zA-Z0-9._-]', '', file.name)
        path = f"{ticket_id}/{ts}_{safe_name}"
        mime = file.type or "application/octet-stream"
        supabase.storage.from_("adjuntos").upload(path, file.getvalue(), {"content-type": mime})
        return supabase.storage.from_("adjuntos").get_public_url(path)
    except Exception as e: return None

def generar_stats_cliente(df, nombre):
    stats = []
    if df.empty: return [{"color": "blue", "titulo": "Bienvenido", "valor": "0 Tickets", "texto": "Crea tu primer caso hoy."}]

    if 'agente_soporte' in df.columns:
        agentes = df[df['agente_soporte'].notnull()]['agente_soporte']
        if not agentes.empty:
            top_agente = agentes.mode()[0]
            if top_agente != "Sin Asignar":
                stats.append({"color": "blue", "titulo": "Tu Agente de Confianza", "valor": top_agente.split()[0], "texto": "Es quien más te ha ayudado."})
    
    if 'modulo_erp' in df.columns:
        modulos = df['modulo_erp']
        if not modulos.empty:
            top_mod = modulos.mode()[0]
            count = len(df[df['modulo_erp'] == top_mod])
            stats.append({"color": "orange", "titulo": "Módulo Crítico", "valor": top_mod, "texto": f"{count} incidencias reportadas."})

    cerrados = len(df[df['estado'].isin(['Resuelto', 'Cerrado'])])
    total = len(df)
    tasa = int((cerrados/total)*100) if total > 0 else 0
    stats.append({"color": "purple", "titulo": "Eficacia de Resolución", "valor": f"{tasa}%", "texto": f"{cerrados} de {total} casos resueltos."})
    return stats

# --- STATE ---
if "user_portal" not in st.session_state: st.session_state["user_portal"] = None

# ================= LOGIN (MODO PORTAFOLIO) =================
if not st.session_state["user_portal"]:
    
    # --- SIDEBAR DEMO ---
    with st.sidebar:
        mostrar_guia_demo() # <--- GUIA AQUI
        
        st.header("👋 Modo Demo")
        st.info("Acceso rápido:")
        if st.button("🚀 Ingresar como Cliente Demo", use_container_width=True):
            st.session_state["user_portal"] = {
                "email": "demo@cliente.com",
                "nombre": "Cliente Visitante",
                "cliente": "Empresa Demo S.A.",
                "activo": True
            }
            registrar_auditoria("demo@cliente.com", "LOGIN_DEMO", "Acceso Demo Portafolio")
            st.rerun()
        st.markdown("---")
        st.caption("© 2026 Developed by Nexus Dev & [Tu Nombre]")
            
    # --- LOGIN NORMAL ---
    c1, c2, c3 = st.columns([1,1,1])
    with c2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.title("🔐 Portal Clientes")
        st.caption("Nexus ERP Support")
        with st.form("login_portal"):
            u = st.text_input("Email Corporativo")
            p = st.text_input("Contraseña", type="password")
            if st.form_submit_button("Ingresar al Portal", use_container_width=True):
                user = login(u, p)
                if user:
                    st.session_state["user_portal"] = user
                    registrar_auditoria(u, "LOGIN", "Acceso al Portal")
                    st.rerun()
                else: st.error("Credenciales inválidas.")

# ================= DASHBOARD CLIENTE =================
else:
    me = st.session_state["user_portal"]
    df = get_my_tickets(me['email'])
    
    # --- HEADER COMPACTO CON LOGO ---
    h1, h2 = st.columns([6, 1])
    with h1:
        st.title("Nexus Portal Clientes")
        st.markdown(f"👋 **Bienvenido:** `{me['nombre']}` | 🏢 `{me['cliente']}`")
    with h2:
        # LOGO DE USUARIO (Simple y limpio)
        st.image("https://cdn-icons-png.flaticon.com/512/9908/9908332.png", width=70)

    st.markdown("---")

    # --- NOTIFICACIONES ---
    if not df.empty:
        pendientes = len(df[df['estado'] == 'Esperando Cliente'])
        if pendientes > 0:
            st.warning(f"🔔 Tienes **{pendientes} ticket(s)** esperando tu respuesta. Por favor revisa 'Mis Tickets'.", icon="⚠️")
    
    # --- SIDEBAR ---
    with st.sidebar:
        mostrar_guia_demo() # <--- GUIA TAMBIEN AQUI
        
        st.title("🏢 Mi Espacio")
        st.write(f"**{me['nombre']}**")
        st.caption(me['cliente'])
        st.markdown("---")
        menu = st.radio("Navegación", ["📊 Mis Estadísticas", "🎫 Mis Tickets", "📝 Nuevo Reclamo", "👤 Mi Perfil"])
        st.markdown("---")
        if st.button("Cerrar Sesión"):
            registrar_auditoria(me['email'], "LOGOUT", "Cierre de sesión")
            st.session_state["user_portal"] = None
            st.rerun()
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.caption("© 2026 Developed by Nexus Dev & [Tu Nombre]")

    # --- 1. ESTADÍSTICAS ---
    if menu == "📊 Mis Estadísticas":
        st.title("Resumen de Actividad")
        stats = generar_stats_cliente(df, me['nombre'])
        c1, c2, c3 = st.columns(3)
        for idx, col in enumerate([c1, c2, c3]):
            if idx < len(stats):
                s = stats[idx]
                col.markdown(f"""<div class="insight-card card-{s['color']}"><div class="insight-title">{s['titulo']}</div><div class="insight-value">{s['valor']}</div><div class="insight-desc">{s['texto']}</div></div>""", unsafe_allow_html=True)
        st.divider()
        if not df.empty:
            g1, g2 = st.columns(2)
            mod_counts = df['modulo_erp'].value_counts().reset_index()
            mod_counts.columns = ['Módulo', 'Cantidad']
            g1.plotly_chart(px.pie(mod_counts, values='Cantidad', names='Módulo', hole=0.4, title="¿Dónde ocurren mis problemas?"), use_container_width=True)
            st_counts = df['estado'].value_counts().reset_index()
            st_counts.columns = ['Estado', 'Cantidad']
            g2.plotly_chart(px.bar(st_counts, x='Cantidad', y='Estado', orientation='h', title="Estado de mis Tickets"), use_container_width=True)

    # --- 2. MIS TICKETS ---
    elif menu == "🎫 Mis Tickets":
        st.title("Gestión de Casos")
        if df.empty: st.info("No tienes tickets registrados.")
        else:
            opciones = df.apply(lambda x: f"{x['id_ticket']} | {x.get('titulo','Sin Asunto')}", axis=1).tolist()
            seleccion = st.selectbox("🔍 Buscar Ticket:", opciones)
            if seleccion:
                tid = seleccion.split(" | ")[0]
                ticket = df[df['id_ticket'] == tid].iloc[0]
                
                c1, c2 = st.columns([3, 1])
                c1.subheader(f"{ticket['titulo']}")
                c2.markdown(f"**Estado:** `{ticket['estado']}`")
                
                st.markdown("#### 💬 Historial de Conversación")
                with st.container(height=500):
                    raw = ticket.get('comentarios', '')
                    if raw:
                        for m in str(raw).split("----------------------------------------"):
                            if not m.strip(): continue
                            meta_text = "Desconocido"; clean_m = m; is_me = False
                            match = re.match(r"\[(.*?)\s-\s(.*?)\]:\n(.*)", m.strip(), re.DOTALL)
                            if match:
                                author_raw = match.group(1).upper()
                                date_raw = match.group(2)
                                clean_m = match.group(3).strip()
                                if "CLIENTE" in author_raw: is_me = True; cls="msg-me"; meta_text=f"👤 Tú ({date_raw})"
                                elif "IA" in author_raw: cls="msg-other"; meta_text=f"🤖 Asistente IA ({date_raw})"
                                else: ag_name = author_raw.replace("AGENTE:", "").strip(); cls="msg-other"; meta_text=f"👮 {ag_name} ({date_raw})"
                            else: cls="msg-other"; meta_text="Mensaje del Sistema"
                            st.markdown(f"<div style='display:flex; flex-direction:column; width:100%;'><div class='msg-box {cls}'><span class='msg-meta'>{meta_text}</span>{clean_m}</div></div>", unsafe_allow_html=True)
                    else: st.info("Inicio del historial.")

                if ticket['estado'] not in ['Cerrado', 'Resuelto']:
                    with st.form("reply_client"):
                        txt = st.text_area("Escribir respuesta...")
                        adj = st.file_uploader("Adjuntar archivo", key="adj_chat")
                        if st.form_submit_button("✉️ Enviar Respuesta"):
                            ts = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
                            txt_extra = ""
                            if adj:
                                url_file = upload_file_storage(adj, tid)
                                if url_file: txt_extra = f"\n\n📎 Archivo adjunto: {url_file}"
                            new_h = f"\n[CLIENTE - {ts}]:\n{txt}{txt_extra}\n\n----------------------------------------\n{raw or ''}"
                            supabase.table("tickets").update({"comentarios": new_h, "estado": "Abierto"}).eq("id_ticket", tid).execute()
                            registrar_auditoria(me['email'], "REPLY", f"Respondió en {tid}")
                            st.success("Mensaje enviado."); time.sleep(1); st.rerun()
                else: st.warning("🔒 Este ticket está cerrado.")

    # --- 3. NUEVO RECLAMO ---
    elif menu == "📝 Nuevo Reclamo":
        st.title("Crear Nueva Solicitud")
        with st.form("create_ticket"):
            c1, c2 = st.columns(2)
            mod = c1.selectbox("Módulo", ["Ventas", "Compras", "Contabilidad", "Stock", "RRHH", "Facturación", "Sistema/Login"])
            prio = c2.select_slider("Urgencia", ["Baja", "Media", "Alta"], value="Media")
            asunto = st.text_input("Asunto")
            desc = st.text_area("Descripción")
            adj = st.file_uploader("Adjuntar Evidencia")
            if st.form_submit_button("🚀 Enviar Ticket"):
                if asunto and desc:
                    nid = f"TK-{int(time.time())}"
                    ts = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
                    url_adj = upload_file_storage(adj, nid) if adj else None
                    init_chat = f"[CLIENTE - {ts}]:\n{desc}\n\n----------------------------------------\n"
                    data = {
                        "id_ticket": nid, "usuario_reportante": me['nombre'], "email_reportante": me['email'],
                        "cliente": me['cliente'], "modulo_erp": mod, "prioridad": prio, "estado": "Abierto",
                        "titulo": asunto, "descripcion": desc, "comentarios": init_chat, "adjuntos": url_adj,
                        "fecha_creacion": datetime.datetime.now().isoformat(), "es_ticket_valido": True
                    }
                    supabase.table("tickets").insert(data).execute()
                    registrar_auditoria(me['email'], "CREATE", f"Creó ticket {nid}")
                    st.success(f"Ticket {nid} creado."); time.sleep(2); st.rerun()
                else: st.error("Faltan datos.")

    # --- 4. PERFIL ---
    elif menu == "👤 Mi Perfil":
        st.title("Mi Cuenta")
        c1, c2 = st.columns(2)
        c1.text_input("Nombre", me['nombre'], disabled=True)
        c2.text_input("Empresa", me['cliente'], disabled=True)
        st.text_input("Email", me['email'], disabled=True)
        
        st.markdown("### 📜 Historial de Actividad")
        st.caption("Registro de tus movimientos en la plataforma.")
        df_audit = get_my_audit(me['email'])
        if not df_audit.empty:
            st.dataframe(df_audit[['fecha', 'accion', 'detalle']], use_container_width=True, hide_index=True)
        else: st.info("Sin actividad reciente.")
        
        st.markdown("### Seguridad")
        with st.form("pass_change"):
            p1 = st.text_input("Nueva Contraseña", type="password")
            p2 = st.text_input("Confirmar Contraseña", type="password")
            if st.form_submit_button("Actualizar Contraseña"):
                if p1 and p1 == p2:
                    supabase.table("reportantes").update({"password": p1}).eq("email", me['email']).execute()
                    registrar_auditoria(me['email'], "CHANGE_PASS", "Cambió clave")
                    st.success("Contraseña actualizada.")
                else: st.error("Las contraseñas no coinciden.")