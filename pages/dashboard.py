import streamlit as st
from supabase import create_client

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

.score-hot  { background:#e63946; color:#fff; padding:3px 12px; border-radius:20px; font-weight:700; font-size:0.8rem; }
.score-warm { background:#f4a261; color:#fff; padding:3px 12px; border-radius:20px; font-weight:700; font-size:0.8rem; }
.score-cold { background:#457b9d; color:#fff; padding:3px 12px; border-radius:20px; font-weight:700; font-size:0.8rem; }

.status-nuevo     { background:#2d6a4f; color:#fff; padding:3px 12px; border-radius:20px; font-size:0.8rem; font-weight:600; }
.status-contactado{ background:#f4a261; color:#fff; padding:3px 12px; border-radius:20px; font-size:0.8rem; font-weight:600; }
.status-visitado  { background:#457b9d; color:#fff; padding:3px 12px; border-radius:20px; font-size:0.8rem; font-weight:600; }
.status-cerrado   { background:#74c69d; color:#1a2e22; padding:3px 12px; border-radius:20px; font-size:0.8rem; font-weight:600; }

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
        supabase.table("leads").update({"status": new_status}).eq("id", lead_id).execute()
    except Exception as e:
        st.error(f"Error actualizando estado: {e}")

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
#  REFRESH BUTTON
# ─────────────────────────────────────────────
if st.button("🔄 Actualizar Leads"):
    st.cache_resource.clear()
    st.rerun()

leads = load_leads()

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
#  FILTER
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

        # Score badge
        if score == "HOT":
            badge = '<span class="score-hot">🔥 HOT</span>'
        elif score == "WARM":
            badge = '<span class="score-warm">⚠️ WARM</span>'
        else:
            badge = '<span class="score-cold">🧊 COLD</span>'

        # Status badge
        status_class = f"status-{status.lower()}"
        status_emoji = {"Nuevo": "🆕", "Contactado": "📞", "Visitado": "🏠", "Cerrado": "✅"}.get(status, "🆕")
        status_badge = f'<span class="{status_class}">{status_emoji} {status}</span>'

        # WhatsApp link
        wa_text = f"Hola {name}, soy de la agencia inmobiliaria LeadBoost. Te contactamos porque mostraste interés en {property_type} en {area}. ¿Tienes un momento para hablar?"
        wa_encoded = wa_text.replace(" ", "%20").replace(",", "%2C").replace("¿", "%C2%BF").replace("?", "%3F")
        wa_link = f"https://wa.me/591{phone}?text={wa_encoded}"

        # Lead card
        st.markdown(f"""
        <div style="background:#1a2e22; border:1px solid #2d6a4f; border-radius:14px;
                    padding:16px 20px; margin-bottom:4px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                <b style="font-size:1rem;">👤 {name}</b>
                <div style="display:flex; gap:8px; align-items:center;">
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

        # Status buttons
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
