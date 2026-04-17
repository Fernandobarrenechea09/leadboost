import streamlit as st
from supabase import create_client
import io
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from datetime import datetime
from urllib.parse import quote

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="LeadBoost - Dashboard",
    page_icon="📊",
    layout="wide"
)

# ─────────────────────────────────────────────
#  CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700&display=swap');
html, body, [class*="css"] {
    font-family: 'Sora', sans-serif;
    background-color: #0e1117;
    color: #f0f0f0;
}
.lb-header {
    background: linear-gradient(135deg, #1a472a 0%, #2d6a4f 100%);
    border-radius: 16px;
    padding: 20px 28px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    gap: 14px;
    box-shadow: 0 4px 24px rgba(0,0,0,0.4);
}
.lb-header h1 { margin: 0; font-size: 1.6rem; color: #fff; }
.lb-header p  { margin: 0; font-size: 0.85rem; color: #b7e4c7; }
.stat-card {
    background: #1a2e22;
    border: 1px solid #2d6a4f;
    border-radius: 16px;
    padding: 20px 24px;
    text-align: center;
}
.stat-card h2 { font-size: 2.2rem; margin: 0; }
.stat-card p  { margin: 4px 0 0 0; font-size: 0.85rem; color: #74c69d; }
.time-card {
    background: #1a2e22;
    border: 1px solid #2d6a4f;
    border-radius: 16px;
    padding: 16px 20px;
    margin-bottom: 8px;
}
.time-card h4 { margin: 0 0 4px 0; color: #74c69d; font-size: 0.85rem; }
.time-card p  { margin: 0; font-size: 1.1rem; font-weight: 600; }
.lead-card {
    background: #1a2e22;
    border: 1px solid #2d6a4f;
    border-radius: 14px;
    padding: 16px 20px;
    margin-bottom: 4px;
}
.lead-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
}
.lead-name { font-size: 1rem; font-weight: 700; }
.lead-badges { display: flex; gap: 8px; align-items: center; }
.lead-grid {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 8px;
    font-size: 0.88rem;
    color: #b7e4c7;
    margin-bottom: 14px;
}
.wa-btn {
    display: inline-block;
    background: #25d366;
    color: #fff;
    padding: 8px 18px;
    border-radius: 10px;
    text-decoration: none;
    font-weight: 600;
    font-size: 0.85rem;
}
.score-hot  { background:#e63946; color:#fff; padding:3px 12px; border-radius:20px; font-weight:700; font-size:0.8rem; }
.score-warm { background:#f4a261; color:#fff; padding:3px 12px; border-radius:20px; font-weight:700; font-size:0.8rem; }
.score-cold { background:#457b9d; color:#fff; padding:3px 12px; border-radius:20px; font-weight:700; font-size:0.8rem; }
.status-nuevo      { background:#2d6a4f; color:#fff; padding:3px 12px; border-radius:20px; font-size:0.8rem; font-weight:600; }
.status-contactado { background:#f4a261; color:#fff; padding:3px 12px; border-radius:20px; font-size:0.8rem; font-weight:600; }
.status-visitado   { background:#457b9d; color:#fff; padding:3px 12px; border-radius:20px; font-size:0.8rem; font-weight:600; }
.status-cerrado    { background:#74c69d; color:#1a2e22; padding:3px 12px; border-radius:20px; font-size:0.8rem; font-weight:600; }
.resp-time { font-size:0.8rem; color:#74c69d; }
div.stButton > button {
    background: linear-gradient(135deg, #2d6a4f, #1b4332);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 10px 28px;
    font-family: 'Sora', sans-serif;
    font-weight: 600;
    font-size: 0.95rem;
}
.stTextInput > div > div > input {
    background: #1a2e22 !important;
    color: #fff !important;
    border: 1px solid #40916c !important;
    border-radius: 12px !important;
    font-family: 'Sora', sans-serif !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  PASSWORD GATE
# ─────────────────────────────────────────────
OWNER_PASSWORD = "leadboost2024"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("""
    <div class="lb-header">
      <div style="font-size:2.2rem">📊</div>
      <div><h1>LeadBoost Dashboard</h1><p>Acceso exclusivo para agentes · Bolivia</p></div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("### 🔒 Ingresa tu contrasena")
    password_input = st.text_input("Contrasena", type="password", label_visibility="collapsed")
    if st.button("Entrar"):
        if password_input == OWNER_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Contrasena incorrecta. Intenta de nuevo.")
    st.stop()

# ─────────────────────────────────────────────
#  SUPABASE
# ─────────────────────────────────────────────
@st.cache_resource
def get_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

def load_leads():
    try:
        return get_supabase().table("leads").select("*").order("id", desc=True).execute().data
    except Exception as e:
        st.error(f"Error cargando leads: {e}")
        return []

def update_status(lead_id, new_status):
    try:
        data = {"status": new_status}
        if new_status == "Contactado":
            data["contacted_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        get_supabase().table("leads").update(data).eq("id", lead_id).execute()
    except Exception as e:
        st.error(f"Error actualizando estado: {e}")

# ─────────────────────────────────────────────
#  RESPONSE TIME HELPERS
# ─────────────────────────────────────────────
def get_minutes(lead):
    try:
        t1 = datetime.strptime(lead.get("timestamp", ""),    "%Y-%m-%d %H:%M")
        t2 = datetime.strptime(lead.get("contacted_at", ""), "%Y-%m-%d %H:%M")
        m  = int((t2 - t1).total_seconds() / 60)
        return m if m >= 0 else None
    except:
        return None

def fmt(minutes):
    if minutes is None: return "—"
    if minutes < 60:    return f"{minutes} min"
    if minutes < 1440:  return f"{round(minutes/60,1)} hrs"
    return f"{round(minutes/1440,1)} dias"

# ─────────────────────────────────────────────
#  EXCEL EXPORT
# ─────────────────────────────────────────────
def generate_excel(leads):
    wb = Workbook()
    ws = wb.active
    ws.title = "LeadBoost Leads"

    h_fill  = PatternFill("solid", fgColor="1B4332")
    hot_f   = PatternFill("solid", fgColor="FADADD")
    warm_f  = PatternFill("solid", fgColor="FFF3CD")
    cold_f  = PatternFill("solid", fgColor="D6EAF8")
    alt_f   = PatternFill("solid", fgColor="F0F7F4")
    border  = Border(left=Side(style="thin",color="CCCCCC"), right=Side(style="thin",color="CCCCCC"),
                     top=Side(style="thin",color="CCCCCC"),  bottom=Side(style="thin",color="CCCCCC"))
    c = Alignment(horizontal="center", vertical="center")
    l = Alignment(horizontal="left",   vertical="center")

    headers = ["#","Fecha","Nombre","Telefono","Tipo Propiedad","Zona","Presupuesto","Plazo","Score","Estado","T. Respuesta"]
    widths  = [5,18,22,15,18,18,16,12,14,14,16]

    for i,(h,w) in enumerate(zip(headers,widths),1):
        cell = ws.cell(row=1,column=i,value=h)
        cell.fill=h_fill; cell.font=Font(bold=True,color="FFFFFF",size=11)
        cell.alignment=c; cell.border=border
        ws.column_dimensions[get_column_letter(i)].width=w
    ws.row_dimensions[1].height=28

    for rn,lead in enumerate(leads,2):
        score = lead.get("score","COLD")
        row_fill = hot_f if score=="HOT" else warm_f if score=="WARM" else (cold_f if rn%2==0 else alt_f)
        minutes  = get_minutes(lead)
        row = [rn-1, lead.get("timestamp",""), lead.get("name",""), lead.get("phone",""),
               lead.get("property_type",""), lead.get("area",""), lead.get("budget",""),
               lead.get("timeline",""), score, lead.get("status","Nuevo"), fmt(minutes)]
        for cn,val in enumerate(row,1):
            cell=ws.cell(row=rn,column=cn,value=val)
            cell.fill=row_fill; cell.border=border
            cell.alignment=c if cn in [1,7,8,9,10,11] else l
            cell.font=Font(bold=True,size=10) if cn==3 else Font(size=10)
        ws.row_dimensions[rn].height=22

    buf=io.BytesIO(); wb.save(buf); buf.seek(0)
    return buf

# ─────────────────────────────────────────────
#  HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="lb-header">
  <div style="font-size:2.2rem">📊</div>
  <div><h1>LeadBoost Dashboard</h1><p>Panel de control · Solo para agentes</p></div>
</div>
""", unsafe_allow_html=True)

leads = load_leads()

# ─────────────────────────────────────────────
#  BUTTONS
# ─────────────────────────────────────────────
b1, b2 = st.columns(2)
with b1:
    if st.button("🔄 Actualizar Leads"):
        st.cache_resource.clear()
        st.rerun()
with b2:
    if leads:
        st.download_button(
            label="⬇️ Exportar Excel",
            data=generate_excel(leads),
            file_name="leadboost_leads.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# ─────────────────────────────────────────────
#  STATS
# ─────────────────────────────────────────────
total = len(leads)
hot   = sum(1 for l in leads if l.get("score")=="HOT")
warm  = sum(1 for l in leads if l.get("score")=="WARM")
cold  = sum(1 for l in leads if l.get("score")=="COLD")

c1,c2,c3,c4 = st.columns(4)
with c1: st.markdown(f'<div class="stat-card"><h2 style="color:#74c69d">{total}</h2><p>Total Leads</p></div>', unsafe_allow_html=True)
with c2: st.markdown(f'<div class="stat-card"><h2 style="color:#e63946">{hot} 🔥</h2><p>HOT Leads</p></div>', unsafe_allow_html=True)
with c3: st.markdown(f'<div class="stat-card"><h2 style="color:#f4a261">{warm} ⚠️</h2><p>WARM Leads</p></div>', unsafe_allow_html=True)
with c4: st.markdown(f'<div class="stat-card"><h2 style="color:#457b9d">{cold} 🧊</h2><p>COLD Leads</p></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  RESPONSE TIME TRACKER
# ─────────────────────────────────────────────
timed = [{"name": l.get("name","—"), "minutes": get_minutes(l)} for l in leads if get_minutes(l) is not None]
if timed:
    st.markdown("### ⏱️ Tiempo de Respuesta")
    avg     = sum(t["minutes"] for t in timed) / len(timed)
    fastest = min(timed, key=lambda x: x["minutes"])
    slowest = max(timed, key=lambda x: x["minutes"])
    t1,t2,t3 = st.columns(3)
    with t1: st.markdown(f'<div class="time-card"><h4>📊 Promedio</h4><p>{fmt(int(avg))}</p></div>', unsafe_allow_html=True)
    with t2: st.markdown(f'<div class="time-card"><h4>🏆 Mas rapido — {fastest["name"]}</h4><p style="color:#74c69d">{fmt(fastest["minutes"])}</p></div>', unsafe_allow_html=True)
    with t3: st.markdown(f'<div class="time-card"><h4>🐢 Mas lento — {slowest["name"]}</h4><p style="color:#f4a261">{fmt(slowest["minutes"])}</p></div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  SEARCH + FILTERS
# ─────────────────────────────────────────────
search = st.text_input("🔍 Buscar por nombre o telefono...", placeholder="Ej: Carlos o 76543210")

f1,f2 = st.columns(2)
with f1: filter_score  = st.selectbox("Filtrar por clasificacion", ["Todos","HOT","WARM","COLD"])
with f2: filter_status = st.selectbox("Filtrar por estado", ["Todos","Nuevo","Contactado","Visitado","Cerrado"])

filtered = leads
if search.strip():
    q = search.strip().lower()
    filtered = [l for l in filtered if q in l.get("name","").lower() or q in l.get("phone","").lower()]
if filter_score  != "Todos": filtered = [l for l in filtered if l.get("score")==filter_score]
if filter_status != "Todos": filtered = [l for l in filtered if l.get("status","Nuevo")==filter_status]

# ─────────────────────────────────────────────
#  LEADS
# ─────────────────────────────────────────────
st.markdown(f"### 📋 Leads ({len(filtered)})")

if not filtered:
    st.info("No hay leads registrados aun.")
else:
    for lead in filtered:
        lead_id  = lead.get("id")
        score    = lead.get("score","COLD")
        status   = lead.get("status","Nuevo")
        name     = lead.get("name","—")
        phone    = lead.get("phone","").replace("+","").replace(" ","").replace("-","")
        ptype    = lead.get("property_type","")
        area     = lead.get("area","")
        budget   = lead.get("budget","—")
        timeline = lead.get("timeline","—")
        ts       = lead.get("timestamp","—")
        minutes  = get_minutes(lead)

        score_badge  = f'<span class="score-{score.lower()}">{"🔥" if score=="HOT" else "⚠️" if score=="WARM" else "🧊"} {score}</span>'
        status_emoji = {"Nuevo":"🆕","Contactado":"📞","Visitado":"🏠","Cerrado":"✅"}.get(status,"🆕")
        status_badge = f'<span class="status-{status.lower()}">{status_emoji} {status}</span>'
        resp_html    = f'<span class="resp-time">⏱️ {fmt(minutes)}</span>' if minutes is not None else ""

        wa_msg  = f"Hola {name}, soy de la agencia LeadBoost. Te contactamos porque mostraste interes en {ptype} en {area}. Tienes un momento para hablar?"
        wa_link = f"https://wa.me/591{phone}?text={quote(wa_msg)}"

        st.markdown(f"""
<div class="lead-card">
  <div class="lead-top">
    <span class="lead-name">👤 {name}</span>
    <div class="lead-badges">{resp_html}{status_badge}{score_badge}</div>
  </div>
  <div class="lead-grid">
    <span>📞 {lead.get('phone','—')}</span>
    <span>🏠 {ptype}</span>
    <span>📍 {area}</span>
    <span>💵 ${budget}</span>
    <span>⏳ {timeline} meses</span>
    <span>🕐 {ts}</span>
  </div>
  <a class="wa-btn" href="{wa_link}" target="_blank">📱 Contactar por WhatsApp</a>
</div>
""", unsafe_allow_html=True)

        cols = st.columns(4)
        for i,s in enumerate(["Nuevo","Contactado","Visitado","Cerrado"]):
            with cols[i]:
                is_current = status == s
                if st.button(f"✓ {s}" if is_current else s, key=f"s_{lead_id}_{s}", disabled=is_current):
                    update_status(lead_id, s)
                    st.rerun()

        st.markdown("<div style='margin-bottom:16px'></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  LOGOUT
# ─────────────────────────────────────────────
st.markdown("---")
if st.button("🚪 Cerrar sesion"):
    st.session_state.authenticated = False
    st.rerun()
