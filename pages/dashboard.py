import streamlit as st
from supabase import create_client
import io
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from datetime import datetime

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="LeadBoost – Dashboard",
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

.score-hot  { background:#e63946; color:#fff; padding:3px 12px; border-radius:20px; font-weight:700; font-size:0.8rem; }
.score-warm { background:#f4a261; color:#fff; padding:3px 12px; border-radius:20px; font-weight:700; font-size:0.8rem; }
.score-cold { background:#457b9d; color:#fff; padding:3px 12px; border-radius:20px; font-weight:700; font-size:0.8rem; }

.status-nuevo      { background:#2d6a4f; color:#fff; padding:3px 12px; border-radius:20px; font-size:0.8rem; font-weight:600; }
.status-contactado { background:#f4a261; color:#fff; padding:3px 12px; border-radius:20px; font-size:0.8rem; font-weight:600; }
.status-visitado   { background:#457b9d; color:#fff; padding:3px 12px; border-radius:20px; font-size:0.8rem; font-weight:600; }
.status-cerrado    { background:#74c69d; color:#1a2e22; padding:3px 12px; border-radius:20px; font-size:0.8rem; font-weight:600; }

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
      <div>
        <h1>LeadBoost Dashboard</h1>
        <p>Acceso exclusivo para agentes · Bolivia</p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🔒 Ingresa tu contraseña")
    password_input = st.text_input("Contraseña", type="password", label_visibility="collapsed")

    if st.button("Entrar"):
        if password_input == OWNER_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("❌ Contraseña incorrecta. Intenta de nuevo.")
    st.stop()

# ─────────────────────────────────────────────
#  SUPABASE CONNECTION
# ─────────────────────────────────────────────
@st.cache_resource
def get_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

# ─────────────────────────────────────────────
#  LOAD LEADS
# ─────────────────────────────────────────────
def load_leads():
    try:
        supabase = get_supabase()
        response = supabase.table("leads").select("*").order("id", desc=True).execute()
        return response.data
    except Exception as e:
        st.error(f"Error cargando leads: {e}")
        return []

# ─────────────────────────────────────────────
#  UPDATE LEAD STATUS
# ─────────────────────────────────────────────
def update_status(lead_id, new_status):
    try:
        supabase = get_supabase()
        update_data = {"status": new_status}
        # Record contact time when marked as Contactado
        if new_status == "Contactado":
            update_data["contacted_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        supabase.table("leads").update(update_data).eq("id", lead_id).execute()
    except Exception as e:
        st.error(f"Error actualizando estado: {e}")

# ─────────────────────────────────────────────
#  RESPONSE TIME CALCULATOR
# ─────────────────────────────────────────────
def calculate_response_times(leads):
    times = []
    for lead in leads:
        timestamp    = lead.get("timestamp")
        contacted_at = lead.get("contacted_at")
        name         = lead.get("name", "—")
        if timestamp and contacted_at:
            try:
                t1    = datetime.strptime(timestamp,    "%Y-%m-%d %H:%M")
                t2    = datetime.strptime(contacted_at, "%Y-%m-%d %H:%M")
                delta = t2 - t1
                minutes = int(delta.total_seconds() / 60)
                if minutes >= 0:
                    times.append({"name": name, "minutes": minutes})
            except:
                pass
    return times

def format_time(minutes):
    if minutes < 60:
        return f"{minutes} min"
    elif minutes < 1440:
        hours = round(minutes / 60, 1)
        return f"{hours} hrs"
    else:
        days = round(minutes / 1440, 1)
        return f"{days} días"

# ─────────────────────────────────────────────
#  GENERATE STYLED EXCEL
# ─────────────────────────────────────────────
def generate_excel(leads):
    wb = Workbook()
    ws = wb.active
    ws.title = "LeadBoost Leads"

    header_fill = PatternFill("solid", fgColor="1B4332")
    hot_fill    = PatternFill("solid", fgColor="FADADD")
    warm_fill   = PatternFill("solid", fgColor="FFF3CD")
    cold_fill   = PatternFill("solid", fgColor="D6EAF8")
    alt_fill    = PatternFill("solid", fgColor="F0F7F4")

    header_font = Font(bold=True, color="FFFFFF", size=11)
    bold_font   = Font(bold=True, size=10)
    normal_font = Font(size=10)

    thin_border = Border(
        left   = Side(style="thin", color="CCCCCC"),
        right  = Side(style="thin", color="CCCCCC"),
        top    = Side(style="thin", color="CCCCCC"),
        bottom = Side(style="thin", color="CCCCCC")
    )

    center = Alignment(horizontal="center", vertical="center")
    left   = Alignment(horizontal="left",   vertical="center")

    headers    = ["#", "Fecha", "Nombre", "Teléfono", "Tipo Propiedad", "Zona", "Presupuesto (USD)", "Plazo (meses)", "Clasificación", "Estado", "Tiempo de Respuesta"]
    col_widths = [5, 18, 22, 15, 18, 18, 18, 14, 14, 14, 20]

    for col_num, (header, width) in enumerate(zip(headers, col_widths), 1):
        cell           = ws.cell(row=1, column=col_num, value=header)
        cell.fill      = header_fill
        cell.font      = header_font
        cell.alignment = center
        cell.border    = thin_border
        ws.column_dimensions[get_column_letter(col_num)].width = width

    ws.row_dimensions[1].height = 28

    for row_num, lead in enumerate(leads, 2):
        score  = lead.get("score", "COLD")
        status = lead.get("status", "Nuevo")

        if score == "HOT":
            row_fill = hot_fill
        elif score == "WARM":
            row_fill = warm_fill
        else:
            row_fill = cold_fill if row_num % 2 == 0 else alt_fill

        score_display  = {"HOT": "🔥 HOT", "WARM": "⚠️ WARM", "COLD": "🧊 COLD"}.get(score, score)
        status_display = {"Nuevo": "🆕 Nuevo", "Contactado": "📞 Contactado", "Visitado": "🏠 Visitado", "Cerrado": "✅ Cerrado"}.get(status, status)

        # Response time
        timestamp    = lead.get("timestamp")
        contacted_at = lead.get("contacted_at")
        response_time = "—"
        if timestamp and contacted_at:
            try:
                t1      = datetime.strptime(timestamp,    "%Y-%m-%d %H:%M")
                t2      = datetime.strptime(contacted_at, "%Y-%m-%d %H:%M")
                minutes = int((t2 - t1).total_seconds() / 60)
                if minutes >= 0:
                    response_time = format_time(minutes)
            except:
                pass

        row_data = [
            row_num - 1,
            lead.get("timestamp", ""),
            lead.get("name", ""),
            lead.get("phone", ""),
            lead.get("property_type", ""),
            lead.get("area", ""),
            lead.get("budget", ""),
            lead.get("timeline", ""),
            score_display,
            status_display,
            response_time,
        ]

        for col_num, value in enumerate(row_data, 1):
            cell           = ws.cell(row=row_num, column=col_num, value=value)
            cell.fill      = row_fill
            cell.border    = thin_border
            cell.alignment = center if col_num in [1, 7, 8, 9, 10, 11] else left
            cell.font      = bold_font if col_num == 3 else normal_font

        ws.row_dimensions[row_num].height = 22

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer

# ─────────────────────────────────────────────
#  HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="lb-header">
  <div style="font-size:2.2rem">📊</div>
  <div>
    <h1>LeadBoost Dashboard</h1>
    <p>Panel de control · Solo para agentes</p>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  BUTTONS ROW
# ─────────────────────────────────────────────
leads = load_leads()

btn_col1, btn_col2 = st.columns([1, 1])

with btn_col1:
    if st.button("🔄 Actualizar Leads"):
        st.cache_resource.clear()
        st.rerun()

with btn_col2:
    if leads:
        excel_buffer = generate_excel(leads)
        st.download_button(
            label     = "⬇️ Exportar Excel",
            data      = excel_buffer,
            file_name = "leadboost_leads.xlsx",
            mime      = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# ─────────────────────────────────────────────
#  STATS ROW
# ─────────────────────────────────────────────
total = len(leads)
hot   = sum(1 for l in leads if l.get("score") == "HOT")
warm  = sum(1 for l in leads if l.get("score") == "WARM")
cold  = sum(1 for l in leads if l.get("score") == "COLD")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f'<div class="stat-card"><h2 style="color:#74c69d">{total}</h2><p>Total Leads</p></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="stat-card"><h2 style="color:#e63946">{hot} 🔥</h2><p>HOT Leads</p></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="stat-card"><h2 style="color:#f4a261">{warm} ⚠️</h2><p>WARM Leads</p></div>', unsafe_allow_html=True)
with col4:
    st.markdown(f'<div class="stat-card"><h2 style="color:#457b9d">{cold} 🧊</h2><p>COLD Leads</p></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  RESPONSE TIME TRACKER
# ─────────────────────────────────────────────
response_times = calculate_response_times(leads)

if response_times:
    st.markdown("### ⏱️ Tiempo de Respuesta")
    avg_minutes = sum(t["minutes"] for t in response_times) / len(response_times)
    fastest     = min(response_times, key=lambda x: x["minutes"])
    slowest     = max(response_times, key=lambda x: x["minutes"])

    rt_col1, rt_col2, rt_col3 = st.columns(3)
    with rt_col1:
        st.markdown(f"""
        <div class="time-card">
            <h4>📊 Promedio</h4>
            <p>{format_time(int(avg_minutes))}</p>
        </div>
        """, unsafe_allow_html=True)
    with rt_col2:
        st.markdown(f"""
        <div class="time-card">
            <h4>🏆 Más rápido — {fastest['name']}</h4>
            <p style="color:#74c69d">{format_time(fastest['minutes'])}</p>
        </div>
        """, unsafe_allow_html=True)
    with rt_col3:
        st.markdown(f"""
        <div class="time-card">
            <h4>🐢 Más lento — {slowest['name']}</h4>
            <p style="color:#f4a261">{format_time(slowest['minutes'])}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  FILTERS
# ─────────────────────────────────────────────
col_f1, col_f2 = st.columns(2)
with col_f1:
    filter_score = st.selectbox("Filtrar por clasificación", ["Todos", "HOT", "WARM", "COLD"])
with col_f2:
    filter_status = st.selectbox("Filtrar por estado", ["Todos", "Nuevo", "Contactado", "Visitado", "Cerrado"])

filtered = leads
if filter_score != "Todos":
    filtered = [l for l in filtered if l.get("score") == filter_score]
if filter_status != "Todos":
    filtered = [l for l in filtered if l.get("status", "Nuevo") == filter_status]

# ─────────────────────────────────────────────
#  LEADS TABLE
# ─────────────────────────────────────────────
st.markdown(f"### 📋 Leads ({len(filtered)})")

if not filtered:
    st.info("No hay leads registrados aún.")
else:
    for lead in filtered:
        lead_id       = lead.get("id")
        score         = lead.get("score", "COLD")
        status        = lead.get("status", "Nuevo")
        name          = lead.get("name", "—")
        phone         = lead.get("phone", "").replace("+", "").replace(" ", "").replace("-", "")
        property_type = lead.get("property_type", "")
        area          = lead.get("area", "")
        timestamp     = lead.get("timestamp")
        contacted_at  = lead.get("contacted_at")

        # Response time per lead
        response_str = ""
        if contacted_at and timestamp:
            try:
                t1      = datetime.strptime(timestamp,    "%Y-%m-%d %H:%M")
                t2      = datetime.strptime(contacted_at, "%Y-%m-%d %H:%M")
                minutes = int((t2 - t1).total_seconds() / 60)
                if minutes >= 0:
                    response_str = f"⏱️ Respondido en {format_time(minutes)}"
            except:
                pass

        if score == "HOT":
            badge = '<span class="score-hot">🔥 HOT</span>'
        elif score == "WARM":
            badge = '<span class="score-warm">⚠️ WARM</span>'
        else:
            badge = '<span class="score-cold">🧊 COLD</span>'

        status_class = f"status-{status.lower()}"
        status_emoji = {"Nuevo": "🆕", "Contactado": "📞", "Visitado": "🏠", "Cerrado": "✅"}.get(status, "🆕")
        status_badge = f'<span class="{status_class}">{status_emoji} {status}</span>'

        wa_text    = f"Hola {name}, soy de la agencia inmobiliaria LeadBoost. Te contactamos porque mostraste interés en {property_type} en {area}. ¿Tienes un momento para hablar?"
        wa_encoded = wa_text.replace(" ", "%20").replace(",", "%2C").replace("¿", "%C2%BF").replace("?", "%3F")
        wa_link    = f"https://wa.me/591{phone}?text={wa_encoded}"

        response_html = f'<span style="font-size:0.8rem; color:#74c69d;">{response_str}</span>' if response_str else ''

        st.markdown(f"""
        <div style="background:#1a2e22; border:1px solid #2d6a4f; border-radius:14px;
                    padding:16px 20px; margin-bottom:4px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                <b style="font-size:1rem;">👤 {name}</b>
                <div style="display:flex; gap:8px; align-items:center;">
                    {response_html}
                    {status_badge}
                    {badge}
                </div>
            </div>
            <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:8px;
                        font-size:0.88rem; color:#b7e4c7; margin-bottom:14px;">
                <span>📞 {lead.get('phone','—')}</span>
                <span>🏠 {property_type}</span>
                <span>📍 {area}</span>
                <span>💵 ${lead.get('budget','—')}</span>
                <span>⏱️ {lead.get('timeline','—')} meses</span>
                <span>🕐 {lead.get('timestamp','—')}</span>
            </div>
            <a href="{wa_link}" target="_blank"
               style="display:inline-block; background:#25d366; color:#fff;
                      padding:8px 18px; border-radius:10px; text-decoration:none;
                      font-weight:600; font-size:0.85rem;">
                📱 Contactar por WhatsApp
            </a>
        </div>
        """, unsafe_allow_html=True)

        STATUS_OPTIONS = ["Nuevo", "Contactado", "Visitado", "Cerrado"]
        cols = st.columns(4)
        for i, s in enumerate(STATUS_OPTIONS):
            with cols[i]:
                is_current = status == s
                label = f"✓ {s}" if is_current else s
                if st.button(label, key=f"status_{lead_id}_{s}", disabled=is_current):
                    update_status(lead_id, s)
                    st.rerun()

        st.markdown("<div style='margin-bottom:16px'></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  LOGOUT
# ─────────────────────────────────────────────
st.markdown("---")
if st.button("🚪 Cerrar sesión"):
    st.session_state.authenticated = False
    st.rerun()
