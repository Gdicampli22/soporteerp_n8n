import streamlit as st
from supabase import create_client, Client
import pandas as pd
import datetime
from datetime import timedelta
import plotly.express as px
import time
import random
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Nexus ERP V9.1", 
    page_icon="📊",
    layout="wide"
)

# --- 2. ESTILOS CSS ---
st.markdown("""
    <style>
    /* General */
    [data-testid="stSidebar"] { background-color: #1e293b; }
    [data-testid="stSidebar"] * { color: #f8fafc !important; }
    
    /* Botones Azules (Legibles) */
    div.stButton > button {
        background-color: #2563eb !important;
        color: #ffffff !important;
        border: 1px solid #1d4ed8;
        border-radius: 6px;
        font-weight: 500;
    }
    div.stButton > button:hover {
        background-color: #1d4ed8 !important;
        color: #ffffff !important;
        border-color: #1e40af;
    }

    /* Kanban Styles */
    div[data-testid="column"] { background-color: #f1f5f9; border-radius: 8px; padding: 8px; border: 1px solid #cbd5e1; min-width: 220px; }
    .kanban-header { font-weight: 900; font-size: 0.9em; margin-bottom: 12px; padding: 8px; border-radius: 4px; text-align: center; color: white; text-transform: uppercase; }
    
    .header-nuevos { background-color: #ef4444; }
    .header-espera { background-color: #f59e0b; }
    .header-proceso { background-color: #3b82f6; }
    .header-revision { background-color: #8b5cf6; }
    .header-resuelto { background-color: #10b981; }

    .kanban-card { background-color: white; padding: 12px; margin-bottom: 10px; border-radius: 6px; box-shadow: 0 1px 2px rgba(0,0,0,0.05); border-left: 4px solid #ccc; cursor: pointer; transition: all 0.15s; font-size: 0.9em; }
    .kanban-card:hover { transform: scale(1.02); box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
    .prio-Alta { border-left-color: #ef4444 !important; }
    .prio-Media { border-left-color: #f59e0b !important; }
    .prio-Baja { border-left-color: #10b981 !important; }
    
    .card-top { display: flex; justify-content: space-between; margin-bottom: 6px; font-size: 0.75em; color: #64748b; }
    .card-id { background: #e2e8f0; padding: 1px 5px; border-radius: 3px; font-family: monospace; font-weight: bold; }
    
    /* Chat Mejorado */
    .msg-box { padding: 10px 14px; border-radius: 10px; font-size: 0.9em; box-shadow: 0 1px 2px rgba(0,0,0,0.05); margin-bottom: 8px; }
    .msg-client { background: white; border-left: 4px solid #f97316; }
    .msg-ai { background: #f0fdf4; border-right: 4px solid #10b981; }
    .msg-human { background: #eff6ff; border-right: 4px solid #3b82f6; }
    .msg-meta { font-size: 0.75em; opacity: 0.7; margin-bottom: 4px; display: block; font-weight: bold; }
    
    /* Insights & Report Cards */
    .insight-card { padding: 15px; border-radius: 12px; color: white; margin-bottom: 10px; min-height: 130px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); position: relative; overflow: hidden; }
    .card-urgent { background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%); }
    .card-tip { background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%); }
    .card-predict { background: linear-gradient(135deg, #7c3aed 0%, #5b21b6 100%); }
    .insight-title { font-weight: bold; font-size: 1.1em; margin-bottom: 8px; display: flex; align-items: center; gap: 8px; }
    .insight-text { font-size: 0.95em; line-height: 1.4; opacity: 0.95; }
    
    </style>
    """, unsafe_allow_html=True)

# --- CONEXIONES ---
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except:
    st.error("⚠️ Configura SUPABASE en secrets.toml")
    st.stop()

# --- FUNCIONES ---

def mostrar_guia_demo():
    """Muestra el instructivo en la sidebar para el portafolio"""
    with st.sidebar.expander("📘 GUÍA DE LA DEMO (Leer Primero)", expanded=False):
        st.markdown("""
        **¡Bienvenido al ecosistema Nexus!**
        Sigue estos pasos para probar el flujo completo:
        
        **1. 📧 El Disparador**
        * Envía un correo real a la dirección configurada en n8n (erpsoporteia@gmail.com).
        * **Asunto:** "Error crítico en facturación"
        * **Cuerpo:** "El sistema se cierra al guardar."
        * *(La IA leerá esto y creará el ticket automáticamente).*
        
        **2. 🕵️‍♂️ El Agente (Tú)**
        * Ingresa como **Agente** o **Admin**.
        * Ve al **Tablero Kanban**.
        * Verás el ticket en "Nuevos".
        * Responde usando la sugerencia de IA.
        
        **3. 🏢 El Cliente**
        * Ve al **Portal Cliente** (app separada).
        * Ingresa con "Cliente Demo".
        * Verás tu respuesta reflejada allí.
        """)

def enviar_respuesta_cliente(destinatario, asunto, cuerpo_respuesta, historial_completo, id_ticket):
    try:
        sender = st.secrets["email"]["sender_email"]
        password = st.secrets["email"]["sender_password"]
        server_smtp = st.secrets["email"]["smtp_server"]
        port = st.secrets["email"]["smtp_port"]

        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = destinatario
        msg['Subject'] = f"Respuesta a Ticket {id_ticket}: {asunto}"

        html_body = f"""
        <html><body style="font-family: Arial, sans-serif; color: #333;">
            <p>{cuerpo_respuesta.replace(chr(10), '<br>')}</p>
            <br><hr><small>Ticket ID: {id_ticket}</small>
        </body></html>
        """
        msg.attach(MIMEText(html_body, 'html'))
        server = smtplib.SMTP(server_smtp, port)
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, destinatario, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        return False

def auth_staff(user, pwd):
    try:
        res = supabase.table("usuarios").select("*").eq("usuario", user).eq("contrasena", pwd).execute()
        if res.data:
            u = res.data[0]
            return {
                "id": u.get("usuario"),
                "nombre": u.get("nombre_agente"),
                "rol": u.get("rol"),
                "email": u.get("usuario"),
                "activo": u.get("activo")
            }
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
                "tickets": ["fecha_creacion", "descripcion", "titulo", "comentarios", "datos_faltantes", "estado", "modulo_erp", "prioridad", "id_ticket", "usuario_reportante", "agente_soporte", "email_reportante"] 
            }
            if table in expected_cols:
                for c in expected_cols[table]:
                    if c not in df.columns: df[c] = "" 
            col_fecha = 'fecha_creacion' if 'fecha_creacion' in df.columns else 'created_at'
            if col_fecha in df.columns:
                df[col_fecha] = pd.to_datetime(df[col_fecha], format='mixed', errors='coerce', utc=True)
                df = df.sort_values(by=col_fecha, ascending=False)
                df['fecha_str'] = df[col_fecha].dt.strftime('%d/%m %H:%M')
                df['fecha_dt'] = df[col_fecha]
        return df
    except: return pd.DataFrame()

def crud_action(table, action, data=None, id_col=None, id_val=None):
    try:
        if action == "update": supabase.table(table).update(data).eq(id_col, id_val).execute()
        elif action == "insert": supabase.table(table).insert(data).execute()
        return True
    except: return False

def obtener_titulo_smart(row):
    tit = row.get('titulo')
    desc = row.get('descripcion')
    if tit and len(str(tit)) > 2: return str(tit)
    if desc: return f"(Auto) {str(desc)[:40]}..."
    return "Sin Asunto"

# --- MOTOR INTELIGENCIA PREDICTIVA ---
def generar_insights_reales(df):
    insights = []
    if df.empty: return [{"tipo": "tip", "titulo": "💡 Sistema en Espera", "texto": "Esperando datos..."}]

    criticos = len(df[df['prioridad'] == 'Alta'])
    now = datetime.datetime.now(datetime.timezone.utc)
    try:
        if 'fecha_dt' in df.columns:
            old_tickets = df[(df['estado'].isin(['Abierto','En Progreso'])) & (df['fecha_dt'] < (now - timedelta(hours=24)))]
            count_old = len(old_tickets)
        else: count_old = 0
    except: count_old = 0

    if criticos > 3: insights.append({"tipo": "urgent", "titulo": "🚨 Colapso Crítico", "texto": f"{criticos} tickets de Alta Prioridad. Activar protocolo de emergencia."})
    elif count_old > 5: insights.append({"tipo": "urgent", "titulo": "⚠️ Riesgo SLA", "texto": f"{count_old} tickets estancados (+24hs)."})
    else: insights.append({"tipo": "urgent", "titulo": "✅ Salud Operativa", "texto": "Niveles óptimos. Sin riesgos inminentes."})

    if 'modulo_erp' in df.columns:
        top_mod = df['modulo_erp'].mode()[0] if not df['modulo_erp'].empty else "Gral"
        count = len(df[df['modulo_erp'] == top_mod])
        pct = int((count/len(df))*100) if len(df)>0 else 0
        if pct > 40: insights.append({"tipo": "predict", "titulo": f"🔥 Foco: {top_mod}", "texto": f"{pct}% de incidencias en {top_mod}. Posible fallo masivo."})
        else: insights.append({"tipo": "predict", "titulo": "🔮 Tendencia Dispersa", "texto": "Incidencias variadas. Sin patrón sistémico."})
    
    tips = ["Limpia la cola de tickets 'Esperando Cliente'.", "Revisa tickets viejos.", "Mantén la calma."]
    insights.append({"tipo": "tip", "titulo": "💡 Consejo", "texto": random.choice(tips)})
    return insights

# --- STATE ---
if "staff" not in st.session_state: st.session_state["staff"] = None
if "view_mode" not in st.session_state: st.session_state["view_mode"] = "kanban"
if "sel_ticket_id" not in st.session_state: st.session_state["sel_ticket_id"] = None
if "draft_reply" not in st.session_state: st.session_state["draft_reply"] = ""

# ================= LOGIN (MODO PORTAFOLIO) =================
if not st.session_state["staff"]:
    
    # --- SIDEBAR PORTAFOLIO ---
    with st.sidebar:
        mostrar_guia_demo() # <--- GUIA AQUI
        
        st.title("🔧 Modo Portafolio")
        st.info("Accesos directos:")
        
        st.markdown("### 👮 Coordinador")
        if st.button("Ingresar como Admin", key="btn_admin", use_container_width=True):
            st.session_state["staff"] = {
                "id": "admin_demo", "nombre": "Admin Demo", 
                "rol": "Coordinador", "email": "admin@nexus.com", "activo": True
            }
            st.rerun()

        st.markdown("### 👨‍💻 Agente")
        if st.button("Ingresar como Agente", key="btn_agente", use_container_width=True):
            st.session_state["staff"] = {
                "id": "agente_demo", "nombre": "Agente Demo", 
                "rol": "Agente", "email": "agente@nexus.com", "activo": True
            }
            st.rerun()
        
        st.markdown("---")
        st.caption("© 2026 Developed by Nexus Dev & [Gastòn Di Campli]")

    # --- LOGIN NORMAL ---
    c1, c2, c3 = st.columns([1,1,1])
    with c2:
        st.title("Nexus Admin")
        with st.form("login"):
            u = st.text_input("Usuario"); p = st.text_input("Contraseña", type="password")
            if st.form_submit_button("Entrar"):
                user = auth_staff(u, p)
                if user: st.session_state["staff"] = user; st.rerun()
                else: st.error("Error credenciales")

# ================= DASHBOARD =================
else:
    user = st.session_state["staff"]
    rol_actual = user['rol']
    nombre_actual = user['nombre']
    
    df_tickets = get_data("tickets")
    df_usuarios = get_data("usuarios")
    es_coordinador = rol_actual in ["Coordinador", "Coordinación", "Admin"]
    
    # --- CABECERA COMPACTA CON LOGO ---
    h1, h2 = st.columns([4, 1])
    with h1:
        st.title("Nexus Control Center")
        st.markdown(f"👤 **Operador:** `{nombre_actual}` | 🛡️ **Rol:** `{rol_actual}` | 🟢 **Estado:** `Online`")
    with h2:
        # LOGO DE SOPORTE/ERP
        st.image("https://cdn-icons-png.flaticon.com/512/4230/4230727.png", width=80)

    st.markdown("---")

    with st.sidebar:
        mostrar_guia_demo() # <--- GUIA TAMBIEN AQUI
        
        st.title("Nexus ERP")
        st.success(f"Hola, {nombre_actual}")
        st.markdown("---")
        menu = st.radio("Menú", ["📋 Tablero (Kanban)", "🧠 Análisis IA", "📈 Reportes", "👥 Gestión Usuarios", "🔍 Explorador"])
        if st.button("Salir"): st.session_state["staff"] = None; st.rerun()
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.caption("© 2026 Developed by Nexus Dev & [Tu Nombre]")

    # ---------------- KANBAN ----------------
    if menu == "📋 Tablero (Kanban)":
        
        # LÓGICA DE FILTRADO PARA KANBAN
        df_kanban = df_tickets.copy()
        
        if es_coordinador:
            # Coordinador puede filtrar en la sidebar
            st.sidebar.markdown("### Filtro Kanban")
            agentes_kanban = ["Todos"] + df_usuarios['nombre_agente'].dropna().unique().tolist()
            sel_kanban = st.sidebar.selectbox("Ver Agente:", agentes_kanban)
            if sel_kanban != "Todos":
                df_kanban = df_kanban[df_kanban['agente_soporte'] == sel_kanban]
        else:
            # Agente solo ve lo suyo o lo sin asignar
            df_kanban = df_kanban[(df_kanban['agente_soporte'] == nombre_actual) | (df_kanban['agente_soporte'].isnull()) | (df_kanban['agente_soporte'] == "Sin Asignar")]

        if st.session_state["view_mode"] == "kanban":
            st.markdown(f"**Viendo {len(df_kanban)} tickets**")
            cols_def = [("Nuevos", ["Sin asignar", "Abierto"], "header-nuevos"), ("En Espera", ["Pendiente de respuesta", "Esperando Cliente"], "header-espera"), ("En Proceso", ["En Progreso"], "header-proceso"), ("Revisión", ["En Revisión"], "header-revision"), ("Finalizados", ["Resuelto", "Cerrado"], "header-resuelto")]
            st_cols = st.columns(len(cols_def))
            
            for idx, (title, statuses, h_cls) in enumerate(cols_def):
                with st_cols[idx]:
                    st.markdown(f"<div class='kanban-header {h_cls}'>{title}</div>", unsafe_allow_html=True)
                    if not df_kanban.empty:
                        for _, r in df_kanban[df_kanban['estado'].isin(statuses)].iterrows():
                            tid = r['id_ticket']
                            mod_safe = r.get('modulo_erp') or "Gral"
                            st.markdown(f"""
                            <div class="kanban-card prio-{r.get('prioridad','Baja')}">
                                <div class="card-top"><span class="card-id">{tid}</span><span>{r.get('usuario_reportante','-')[:15]}</span></div>
                                <div style="font-weight:600; margin-bottom:5px;">{obtener_titulo_smart(r)}</div>
                                <div style="display:flex; justify-content:space-between; font-size:0.8em; color:#666;">
                                   <span>📂 {str(mod_safe)[:10]}</span><span>👮 {str(r.get('agente_soporte','-')).split()[0]}</span>
                                </div>
                            </div>""", unsafe_allow_html=True)
                            if st.button("Ver", key=f"k_{tid}", use_container_width=True):
                                st.session_state["sel_ticket_id"] = tid; st.session_state["view_mode"] = "detail"; st.rerun()

        elif st.session_state["view_mode"] == "detail":
            t = df_tickets[df_tickets['id_ticket'] == st.session_state["sel_ticket_id"]].iloc[0]
            c1, c2 = st.columns([2, 1])
            with c1:
                st.subheader(f"{t['id_ticket']} | {t['usuario_reportante']}")
                with st.container(height=500):
                    raw = t.get('comentarios', '')
                    if raw:
                        for m in str(raw).split("----------------------------------------"):
                            if not m.strip(): continue
                            meta_text = "Desconocido"
                            clean_m = m
                            match = re.match(r"\[(.*?)\s-\s(.*?)\]:\n(.*)", m.strip(), re.DOTALL)
                            if match:
                                author_raw = match.group(1).upper()
                                date_raw = match.group(2)
                                clean_m = match.group(3).strip()
                                if "CLIENTE" in author_raw: cls="msg-client"; al="flex-start"; meta_text=f"👤 Cliente ({date_raw})"
                                elif "IA" in author_raw: cls="msg-ai"; al="flex-end"; meta_text=f"🤖 Copilot ({date_raw})"
                                elif "AGENTE" in author_raw: 
                                    an = author_raw.replace("AGENTE:", "").strip()
                                    cls="msg-human"; al="flex-end"; meta_text=f"👮 {an} ({date_raw})"
                                else: cls="msg-human"; al="flex-end"; meta_text=f"👮 Staff ({date_raw})"
                            else: cls="msg-human"; al="flex-end"; meta_text="Mensaje"
                            st.markdown(f"<div style='display:flex; justify-content:{al}'><div class='msg-box {cls}'><span class='msg-meta'>{meta_text}</span>{clean_m}</div></div>", unsafe_allow_html=True)

                with st.form("reply"):
                    txt = st.text_area("Responder:", value=st.session_state.get('draft_reply',''))
                    if st.form_submit_button("✉️ Enviar"):
                        ts = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
                        email_dest = t.get('email_reportante')
                        if email_dest and "@" in str(email_dest):
                            enviar_respuesta_cliente(email_dest, t.get('titulo'), txt, raw, t['id_ticket'])
                            st.toast("Email enviado")
                        new_h = f"\n[AGENTE: {nombre_actual} - {ts}]:\n{txt}\n\n----------------------------------------\n{raw or ''}"
                        crud_action("tickets", "update", {"comentarios": new_h, "estado": "Esperando Cliente", "agente_soporte": nombre_actual}, "id_ticket", t['id_ticket'])
                        st.session_state['draft_reply'] = ""; time.sleep(1); st.rerun()

            with c2:
                if st.button("🔙 Volver"): st.session_state["view_mode"] = "kanban"; st.rerun()
                st.markdown("#### ⚙️ Gestión")
                ag = t.get('agente_soporte') or "Sin Asignar"
                lst_ag = ["Sin Asignar"] + df_usuarios['nombre_agente'].dropna().unique().tolist()
                new_ag = st.selectbox("Asignado:", lst_ag, index=lst_ag.index(ag) if ag in lst_ag else 0)
                st.divider()
                lst_st = ["Abierto", "En Progreso", "Esperando Cliente", "En Revisión", "Resuelto", "Cerrado"]
                ne = st.selectbox("Estado", lst_st, index=lst_st.index(t.get('estado')) if t.get('estado') in lst_st else 0)
                lst_pr = ["Baja", "Media", "Alta"]
                np = st.selectbox("Prioridad", lst_pr, index=lst_pr.index(t.get('prioridad')) if t.get('prioridad') in lst_pr else 1)
                nm = st.text_input("Módulo", value=t.get('modulo_erp',''))
                if st.button("💾 Guardar"):
                    crud_action("tickets", "update", {"estado": ne, "agente_soporte": new_ag, "prioridad": np, "modulo_erp": nm}, "id_ticket", t['id_ticket'])
                    st.success("Guardado"); time.sleep(1); st.rerun()

    # ---------------- ANALISIS IA (BI MEJORADO) ----------------
    elif menu == "🧠 Análisis IA":
        st.title("Centro de Inteligencia (BI)")
        
        df_analisis = df_tickets.copy()
        
        # --- FILTRO INTELIGENTE SEGÚN ROL ---
        if es_coordinador:
            # Coordinador ve todo y filtra
            st.markdown("### 🔭 Visión Global de Equipo")
            c_filtro, _ = st.columns([1, 3])
            lista_agentes = ["(Todos los Agentes)"] + df_usuarios['nombre_agente'].dropna().unique().tolist()
            sel_agente = c_filtro.selectbox("Filtrar métricas por:", lista_agentes)
            
            if sel_agente != "(Todos los Agentes)":
                df_analisis = df_analisis[df_analisis['agente_soporte'] == sel_agente]
                st.info(f"🔍 Analizando desempeño específico de: **{sel_agente}**")
        else:
            # Agente solo ve lo suyo (Sin opción de cambiar)
            st.markdown(f"### 👋 Tablero Personal: {nombre_actual}")
            df_analisis = df_analisis[df_analisis['agente_soporte'] == nombre_actual]
            st.info("🔒 Visualizando únicamente tus tickets asignados.")

        if df_analisis.empty: 
            st.warning("No hay datos para mostrar con los filtros actuales.")
        else:
            # INSIGHTS & KPIS
            insights = generar_insights_reales(df_analisis)
            cc1, cc2, cc3 = st.columns(3)
            for k, col in enumerate([cc1, cc2, cc3]):
                if k < len(insights):
                    i = insights[k]
                    col.markdown(f"""<div class="insight-card card-{i['tipo']}"><div class="insight-title">{i['titulo']}</div><div class="insight-text">{i['texto']}</div></div>""", unsafe_allow_html=True)
            
            st.markdown("---")
            
            total = len(df_analisis)
            resueltos = len(df_analisis[df_analisis['estado'].isin(['Resuelto', 'Cerrado'])])
            abiertos = len(df_analisis[df_analisis['estado'] == 'Abierto'])
            tasa = int((resueltos/total)*100) if total > 0 else 0
            
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Total Tickets", total)
            k2.metric("Tasa Resolución", f"{tasa}%")
            k3.metric("Pendientes (Cola)", abiertos, delta_color="inverse")
            k4.metric("Alta Prioridad", len(df_analisis[df_analisis['prioridad'] == 'Alta']), delta="Alert")
            
            st.markdown("### 📊 Métricas Visuales")
            g1, g2 = st.columns(2)
            g1.plotly_chart(px.pie(df_analisis, names='estado', hole=0.4, title="Distribución por Estado"), use_container_width=True)
            g2.plotly_chart(px.bar(df_analisis, x='prioridad', title="Volumen por Prioridad", color='prioridad', 
                                   color_discrete_map={'Alta':'red', 'Media':'orange', 'Baja':'green'}), use_container_width=True)
            
            g3, g4 = st.columns(2)
            g3.plotly_chart(px.bar(df_analisis['modulo_erp'].value_counts(), orientation='h', title="Fallas por Módulo"), use_container_width=True)
            
            if 'fecha_dt' in df_analisis.columns:
                df_time = df_analisis.groupby(df_analisis['fecha_dt'].dt.date).size().reset_index(name='count')
                g4.plotly_chart(px.line(df_time, x='fecha_dt', y='count', title="Evolución de Tickets (Diario)"), use_container_width=True)

    # ---------------- REPORTES (AMPLIADO) ----------------
    elif menu == "📈 Reportes":
        st.title("Centro de Reportes")
        
        with st.expander("🛠️ Configuración", expanded=True):
            c1, c2, c3 = st.columns(3)
            # NUEVOS REPORTES AGREGADOS AQUI
            tipo_rep = c1.selectbox("Tipo de Reporte", [
                "Rendimiento General", 
                "Carga de Trabajo (Agentes)", 
                "Tickets Críticos",
                "Auditoría de Seguridad"
            ])
            f_inicio = c2.date_input("Desde", datetime.date.today() - datetime.timedelta(days=30))
            f_fin = c3.date_input("Hasta", datetime.date.today())
            
            filtro_agente = "Todos"
            # Lógica de Permiso de Reporte (Coordinador vs Agente)
            if es_coordinador and tipo_rep not in ["Auditoría de Seguridad", "Carga de Trabajo (Agentes)"]:
                lista_ags = ["Todos"] + df_usuarios['nombre_agente'].dropna().unique().tolist()
                filtro_agente = st.selectbox("Filtrar por Agente", lista_ags)
            elif not es_coordinador:
                filtro_agente = nombre_actual

        if st.button("📊 Generar Informe"):
            st.markdown("---")
            
            # --- 1. RENDIMIENTO GENERAL ---
            if tipo_rep == "Rendimiento General":
                mask = (df_tickets['fecha_creacion'].dt.date >= f_inicio) & (df_tickets['fecha_creacion'].dt.date <= f_fin)
                df_rep = df_tickets.loc[mask]
                if filtro_agente != "Todos": df_rep = df_rep[df_rep['agente_soporte'] == filtro_agente]
                
                if df_rep.empty: st.warning("Sin datos.")
                else:
                    st.subheader(f"📑 Reporte de Rendimiento ({filtro_agente})")
                    st.dataframe(df_rep[['id_ticket', 'fecha_str', 'titulo', 'prioridad', 'estado', 'usuario_reportante']], use_container_width=True)
                    csv = df_rep.to_csv(index=False).encode('utf-8')
                    st.download_button("📥 Descargar CSV", csv, "reporte_rendimiento.csv", "text/csv")

            # --- 2. CARGA DE TRABAJO (NUEVO) ---
            elif tipo_rep == "Carga de Trabajo (Agentes)":
                if not es_coordinador:
                    st.error("Acceso denegado. Este reporte es solo para Coordinación.")
                else:
                    st.subheader("⚖️ Distribución de Carga por Agente")
                    # Agrupar por agente y estado
                    df_load = df_tickets.groupby(['agente_soporte', 'estado']).size().reset_index(name='tickets')
                    st.plotly_chart(px.bar(df_load, x="agente_soporte", y="tickets", color="estado", title="Tickets Asignados por Agente"), use_container_width=True)
                    
                    # Tabla resumen
                    pivot = pd.crosstab(df_tickets['agente_soporte'], df_tickets['estado'])
                    st.dataframe(pivot, use_container_width=True)
                    csv = pivot.to_csv().encode('utf-8')
                    st.download_button("📥 Descargar Matriz de Carga", csv, "carga_agentes.csv", "text/csv")

            # --- 3. TICKETS CRÍTICOS ---
            elif tipo_rep == "Tickets Críticos":
                df_crit = df_tickets[ (df_tickets['prioridad'] == 'Alta') & (df_tickets['estado'] != 'Cerrado') ]
                if filtro_agente != "Todos": df_crit = df_crit[df_crit['agente_soporte'] == filtro_agente]
                
                if df_crit.empty: st.success("✅ No hay tickets críticos pendientes.")
                else:
                    st.subheader("🔥 Tickets de Alta Prioridad Pendientes")
                    st.dataframe(df_crit[['id_ticket', 'titulo', 'agente_soporte', 'fecha_str']], use_container_width=True)
                    csv = df_crit.to_csv(index=False).encode('utf-8')
                    st.download_button("📥 Descargar Críticos", csv, "reporte_criticos.csv", "text/csv")

            # --- 4. AUDITORÍA ---
            elif tipo_rep == "Auditoría de Seguridad":
                if not es_coordinador: st.error("Acceso restringido a Coordinación.")
                else:
                    df_audit = get_data("auditoria")
                    if not df_audit.empty:
                        st.subheader("🛡️ Registro de Actividad Global")
                        st.dataframe(df_audit, use_container_width=True)
                        csv = df_audit.to_csv(index=False).encode('utf-8')
                        st.download_button("📥 Descargar Logs", csv, "auditoria.csv", "text/csv")
                    else: st.warning("Sin registros.")

    # ---------------- GESTIÓN USUARIOS ----------------
    elif menu == "👥 Gestión Usuarios":
        st.title("Administración")
        t1, t2 = st.tabs(["🏭 Clientes", "🏢 Staff"])
        with t1:
            dr = get_data("reportantes")
            c1, c2 = st.columns([3,1])
            c1.dataframe(dr[['email','nombre','cliente','activo']], use_container_width=True)
            with c2:
                with st.form("new_cli"):
                    e=st.text_input("Email"); p=st.text_input("Pass"); n=st.text_input("Nombre"); c=st.text_input("Empresa")
                    if st.form_submit_button("Crear"):
                        crud_action("reportantes", "insert", {"email":e, "password":p, "nombre":n, "cliente":c, "activo":True})
                        st.rerun()
        with t2:
            du = get_data("usuarios")
            c1, c2 = st.columns([3,1])
            c1.dataframe(du[['usuario','nombre_agente','rol','activo']], use_container_width=True)
            with c2:
                with st.form("new_staff"):
                    u=st.text_input("User"); p=st.text_input("Pass"); n=st.text_input("Nombre"); r=st.selectbox("Rol", ["Agente","Coordinador"])
                    if st.form_submit_button("Crear"):
                        crud_action("usuarios", "insert", {"usuario":u, "email":u, "contrasena":p, "nombre_agente":n, "rol":r, "activo":True})
                        st.rerun()

    # ---------------- EXPLORADOR ----------------
    elif menu == "🔍 Explorador":
        st.title("Explorador de Datos")
        st.dataframe(df_tickets, use_container_width=True)