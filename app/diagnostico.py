import streamlit as st
from supabase import create_client, Client
import pandas as pd
import datetime
import plotly.express as px
import time
import random
import re

# --- 1. CONFIGURACIÓN DE PÁGINA (TITULO FORZADO) ---
st.set_page_config(
    page_title="NEXUS V4 - FINAL", # <--- SI NO VES ESTO EN LA PESTAÑA, ES CACHE
    page_icon="🚀",
    layout="wide"
)

# --- 2. ESTILOS CSS AGRESIVOS (PARA VER EL CAMBIO) ---
st.markdown("""
    <style>
    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #1e293b; }
    [data-testid="stSidebar"] * { color: #f8fafc !important; }
    
    /* Kanban Styles - 5 COLUMNAS */
    div[data-testid="column"] {
        background-color: #f1f5f9;
        border-radius: 8px;
        padding: 8px;
        border: 1px solid #cbd5e1;
        min-width: 220px;
    }
    .kanban-header {
        font-weight: 900; font-size: 0.9em; margin-bottom: 12px; padding: 8px;
        border-radius: 4px; text-align: center; color: white;
        text-transform: uppercase; letter-spacing: 0.05em;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    /* Colores de cabecera de columna */
    .header-nuevos { background-color: #64748b; }
    .header-espera { background-color: #f59e0b; }
    .header-proceso { background-color: #3b82f6; }
    .header-revision { background-color: #8b5cf6; }
    .header-resuelto { background-color: #10b981; }

    .kanban-card {
        background-color: white; padding: 12px; margin-bottom: 10px; border-radius: 6px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05); border-left: 4px solid #ccc;
        cursor: pointer; transition: all 0.15s; font-size: 0.9em;
    }
    .kanban-card:hover { transform: scale(1.02); box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
    
    .prio-Alta { border-left-color: #ef4444 !important; }
    .prio-Media { border-left-color: #f59e0b !important; }
    .prio-Baja { border-left-color: #10b981 !important; }
    
    /* DATOS EN TARJETA */
    .card-top { display: flex; justify-content: space-between; margin-bottom: 6px; font-size: 0.75em; color: #64748b; }
    .card-id { background: #e2e8f0; padding: 1px 5px; border-radius: 3px; font-family: monospace; font-weight: bold; }
    .card-client { font-weight: bold; color: #334155; }
    
    /* Chat Styles */
    .msg-box { padding: 10px 14px; border-radius: 10px; font-size: 0.9em; box-shadow: 0 1px 2px rgba(0,0,0,0.05); margin-bottom: 6px; }
    .msg-client { background: white; border-left: 4px solid #f97316; }
    .msg-staff { background: #eff6ff; border-right: 4px solid #3b82f6; }
    .msg-system { background: #f8fafc; border: 1px dashed #cbd5e1; font-size: 0.8em; text-align: center; font-style: italic; color: #64748b; }
    </style>
    """, unsafe_allow_html=True)

# --- CONEXIÓN SUPABASE ---
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except:
    st.error("⚠️ Error Crítico: No se encontraron credenciales en .streamlit/secrets.toml")
    st.stop()

# --- FUNCIONES ---
def registrar_auditoria(usuario, accion, detalle, entidad):
    try:
        data = { "usuario_responsable": usuario, "accion": accion, "detalle": detalle, "entidad": entidad, "fecha": datetime.datetime.now().isoformat() }
        supabase.table("auditoria").insert(data).execute()
    except: pass

def auth_staff(user, pwd):
    try:
        res = supabase.table("usuarios").select("*").eq("usuario", user).eq("contrasena", pwd).execute()
        if res.data:
            u = res.data[0]
            return {"id": u.get("usuario"), "nombre": u.get("nombre_agente"), "rol": u.get("rol"), "email": u.get("usuario")}
        return None
    except: return None

def get_data(table):
    try:
        res = supabase.table(table).select("*").execute()
        df = pd.DataFrame(res.data)
        if not df.empty:
            expected_cols = {
                "usuarios": ["activo", "nombre_agente", "rol"],
                "reportantes": ["cliente", "activo", "telefono", "empresa"],
                "tickets": ["fecha_creacion", "created_at", "descripcion", "titulo", "comentarios", "datos_faltantes", "estado", "modulo_erp", "prioridad", "id_ticket", "usuario_reportante", "agente_soporte"] 
            }
            if table in expected_cols:
                for c in expected_cols[table]:
                    if c not in df.columns: df[c] = "" 
            
            # Fechas
            col_fecha = None
            if 'fecha_creacion' in df.columns: col_fecha = 'fecha_creacion'
            elif 'created_at' in df.columns: col_fecha = 'created_at'
            elif 'fecha' in df.columns: col_fecha = 'fecha'

            if col_fecha:
                df[col_fecha] = pd.to_datetime(df[col_fecha], format='mixed', errors='coerce', utc=True)
                df = df.sort_values(by=col_fecha, ascending=False)
                df['fecha_str'] = df[col_fecha].dt.strftime('%d/%m %H:%M')
                df['fecha_dt'] = df[col_fecha]
        return df
    except: return pd.DataFrame()

def crud_action(table, action, data=None, id_col=None, id_val=None):
    try:
        if action == "insert": supabase.table(table).insert(data).execute()
        elif action == "update": supabase.table(table).update(data).eq(id_col, id_val).execute()
        return True
    except Exception as e:
        st.error(f"Error DB: {e}"); return False

def obtener_titulo_smart(row):
    tit = row.get('titulo')
    desc = row.get('descripcion')
    com = row.get('comentarios')
    if tit and len(str(tit).strip()) > 1 and str(tit).lower() != "none": return str(tit)
    elif desc and len(str(desc).strip()) > 1: return f"(Auto) {str(desc).replace(chr(10), ' ')[:40]}..."
    elif com and len(str(com).strip()) > 1:
        clean = re.sub(r'\[.*?\]:\n', '', str(com)).replace("\n", " ").strip()
        return f"(Email) {clean[:40]}..."
    else: return "Ticket Sin Asunto"

# --- STATE ---
if "staff" not in st.session_state: st.session_state["staff"] = None
if "view_mode" not in st.session_state: st.session_state["view_mode"] = "kanban"
if "sel_ticket_id" not in st.session_state: st.session_state["sel_ticket_id"] = None
if "draft_reply" not in st.session_state: st.session_state["draft_reply"] = ""

# ================= LOGIN =================
if not st.session_state["staff"]:
    c1, c2, c3 = st.columns([1,1,1])
    with c2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.title("Nexus V4")
        with st.form("login"):
            u = st.text_input("Usuario"); p = st.text_input("Contraseña", type="password")
            if st.form_submit_button("Entrar"):
                user = auth_staff(u, p)
                if user: st.session_state["staff"] = user; st.rerun()
                else: st.error("Credenciales incorrectas")

# ================= DASHBOARD =================
else:
    user = st.session_state["staff"]
    rol_actual = user['rol']
    nombre_actual = user['nombre']
    
    df_tickets = get_data("tickets")
    df_usuarios = get_data("usuarios")
    
    with st.sidebar:
        st.title("Nexus ERP")
        st.success("✅ VERSIÓN V4 ACTIVA") # INDICADOR DE QUE FUNCIONA
        st.caption(f"Agente: {nombre_actual}")
        st.markdown("---")
        
        menu = st.radio("Menú", [
            "📋 Tablero (Kanban)",
            "🔍 Explorador (Grilla)", 
            "🧠 Métricas",
            "👥 Usuarios",
            "🛡️ Auditoría"
        ])
        
        if st.button("Cerrar Sesión"): st.session_state["staff"] = None; st.rerun()

    # ---------------- 1. KANBAN (5 COLUMNAS REALES) ----------------
    if menu == "📋 Tablero (Kanban)":
        h1, h2 = st.columns([6,1])
        h1.title("Tablero de Operaciones")
        if st.session_state["view_mode"] == "detail":
            if h2.button("🔙 Volver"): st.session_state["view_mode"] = "kanban"; st.session_state["sel_ticket_id"] = None; st.rerun()

        if st.session_state["view_mode"]