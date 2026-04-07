import streamlit as st
import csv
import os

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
OWNER_PASSWORD = "leadboost2024"   # ← Change this to your own password

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
#  LOAD LEADS FROM CSV
# ─────────────────────────────────────────────
def load_leads():
    filepath = "leads.csv"
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)

leads = load_leads()

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
#  STATS ROW
# ─────────────────────────────────────────────
total = len(leads)
hot   = sum(1 for l in leads if l.get("score") == "HOT")
warm  = sum(1 for l in leads if l.get("score") == "WARM")
cold  = sum(1 for l in leads if l.get("score") == "COLD")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="stat-card">
        <h2 style="color:#74c69d">{total}</h2>
        <p>Total Leads</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="stat-card">
        <h2 style="color:#e63946">{hot} 🔥</h2>
        <p>HOT Leads</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="stat-card">
        <h2 style="color:#f4a261">{warm} ⚠️</h2>
        <p>WARM Leads</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="stat-card">
        <h2 style="color:#457b9d">{cold} 🧊</h2>
        <p>COLD Leads</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  FILTER
# ─────────────────────────────────────────────
filter_score = st.selectbox(
    "Filtrar por clasificación",
    ["Todos", "HOT", "WARM", "COLD"],
    index=0
)

filtered = leads if filter_score == "Todos" else [l for l in leads if l.get("score") == filter_score]

# ─────────────────────────────────────────────
#  LEADS TABLE
# ─────────────────────────────────────────────
st.markdown(f"### 📋 Leads ({len(filtered)})")

if not filtered:
    st.info("No hay leads registrados aún.")
else:
    for lead in reversed(filtered):  # newest first
        score = lead.get("score", "COLD")

        if score == "HOT":
            badge = '<span class="score-hot">🔥 HOT</span>'
        elif score == "WARM":
            badge = '<span class="score-warm">⚠️ WARM</span>'
        else:
            badge = '<span class="score-cold">🧊 COLD</span>'

        st.markdown(f"""
        <div style="background:#1a2e22; border:1px solid #2d6a4f; border-radius:14px;
                    padding:16px 20px; margin-bottom:12px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                <b style="font-size:1rem;">👤 {lead.get('name','—')}</b>
                {badge}
            </div>
            <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:8px; font-size:0.88rem; color:#b7e4c7;">
                <span>📞 {lead.get('phone','—')}</span>
                <span>🏠 {lead.get('property_type','—')}</span>
                <span>📍 {lead.get('area','—')}</span>
                <span>💵 ${lead.get('budget','—')}</span>
                <span>⏱️ {lead.get('timeline','—')} meses</span>
                <span>🕐 {lead.get('timestamp','—')}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  LOGOUT
# ─────────────────────────────────────────────
st.markdown("---")
if st.button("🚪 Cerrar sesión"):
    st.session_state.authenticated = False
    st.rerun()
