import streamlit as st
from supabase import create_client
from datetime import datetime

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="LeadBoost – Asistente Inmobiliario",
    page_icon="🏠",
    layout="centered"
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

.chat-wrap { display: flex; flex-direction: column; gap: 10px; margin-bottom: 20px; }

.bubble-bot {
    background: #1e3a2f;
    border: 1px solid #2d6a4f;
    border-radius: 0px 18px 18px 18px;
    padding: 12px 16px;
    max-width: 80%;
    align-self: flex-start;
    font-size: 0.95rem;
    line-height: 1.5;
    color: #d8f3dc;
}

.bubble-user {
    background: #25503d;
    border: 1px solid #40916c;
    border-radius: 18px 18px 0px 18px;
    padding: 12px 16px;
    max-width: 80%;
    align-self: flex-end;
    font-size: 0.95rem;
    line-height: 1.5;
    color: #fff;
}

.label-bot  { font-size: 0.7rem; color: #74c69d; margin-bottom: 3px; }
.label-user { font-size: 0.7rem; color: #95d5b2; margin-bottom: 3px; text-align: right; }

.stTextInput > div > div > input {
    background: #1a2e22 !important;
    color: #fff !important;
    border: 1px solid #40916c !important;
    border-radius: 12px !important;
    padding: 12px 16px !important;
    font-family: 'Sora', sans-serif !important;
}
div.stButton > button {
    background: linear-gradient(135deg, #2d6a4f, #1b4332);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 10px 28px;
    font-family: 'Sora', sans-serif;
    font-weight: 600;
    font-size: 0.95rem;
    cursor: pointer;
    transition: opacity 0.2s;
}
div.stButton > button:hover { opacity: 0.85; }
.stTextInput label { color: #74c69d !important; font-size: 0.85rem !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  SUPABASE CONNECTION
# ─────────────────────────────────────────────
@st.cache_resource
def get_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

# ─────────────────────────────────────────────
#  CONVERSATION STEPS
# ─────────────────────────────────────────────
STEPS = [
    {
        "key":      "name",
        "question": "👋 ¡Hola! Soy LeadBoost, tu asistente inmobiliario virtual.\n\nPara comenzar, ¿cuál es tu nombre?",
        "label":    "Tu nombre completo",
    },
    {
        "key":      "property_type",
        "question": "¿Qué tipo de propiedad estás buscando?\n\n🏠 Casa  |  🏢 Departamento  |  🏗️ Terreno  |  🏪 Local comercial",
        "label":    "Tipo de propiedad",
    },
    {
        "key":      "area",
        "question": "¿En qué zona o barrio de la ciudad te interesa la propiedad?",
        "label":    "Zona o barrio preferido",
    },
    {
        "key":      "budget",
        "question": "¿Cuál es tu presupuesto aproximado en dólares?\n\nEjemplo: 80000  o  150000",
        "label":    "Presupuesto en USD",
    },
    {
        "key":      "timeline",
        "question": "¿En cuántos meses planeas comprar o rentar?\n\nEjemplo: 1  o  3  o  12",
        "label":    "Plazo en meses",
    },
    {
        "key":      "phone",
        "question": "¡Perfecto! Por último, ¿cuál es tu número de teléfono para que un agente te contacte?",
        "label":    "Número de teléfono",
    },
]

# ─────────────────────────────────────────────
#  SESSION STATE INIT
# ─────────────────────────────────────────────
if "step"         not in st.session_state: st.session_state.step         = 0
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "lead"         not in st.session_state: st.session_state.lead         = {}
if "done"         not in st.session_state: st.session_state.done         = False
if "greeted"      not in st.session_state: st.session_state.greeted      = False

# ─────────────────────────────────────────────
#  LEAD SCORING
# ─────────────────────────────────────────────
def score_lead(lead):
    try:
        budget   = int(str(lead.get("budget", "0")).replace(",", "").replace(".", "").replace("$", "").strip())
        timeline = int(str(lead.get("timeline", "99")).strip())
    except ValueError:
        return "COLD"
    if budget >= 80000 and timeline <= 2:
        return "HOT"
    elif budget >= 40000 and timeline <= 6:
        return "WARM"
    else:
        return "COLD"

# ─────────────────────────────────────────────
#  SAVE LEAD TO SUPABASE
# ─────────────────────────────────────────────
def save_lead(lead):
    try:
        supabase = get_supabase()
        supabase.table("leads").insert({
            "timestamp":     datetime.now().strftime("%Y-%m-%d %H:%M"),
            "name":          lead.get("name", ""),
            "phone":         lead.get("phone", ""),
            "property_type": lead.get("property_type", ""),
            "area":          lead.get("area", ""),
            "budget":        lead.get("budget", ""),
            "timeline":      lead.get("timeline", ""),
            "score":         lead.get("score", ""),
        }).execute()
    except Exception as e:
        st.error(f"Error guardando lead: {e}")

# ─────────────────────────────────────────────
#  HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="lb-header">
  <div style="font-size:2.2rem">🏠</div>
  <div>
    <h1>LeadBoost</h1>
    <p>Asistente Inmobiliario Inteligente · Bolivia</p>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  FIRST BOT MESSAGE
# ─────────────────────────────────────────────
if not st.session_state.greeted:
    st.session_state.chat_history.append(("bot", STEPS[0]["question"]))
    st.session_state.greeted = True

# ─────────────────────────────────────────────
#  RENDER CHAT HISTORY
# ─────────────────────────────────────────────
st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)
for sender, msg in st.session_state.chat_history:
    msg_html = msg.replace("\n", "<br>")
    if sender == "bot":
        st.markdown(f'<div class="label-bot">🤖 LeadBoost</div><div class="bubble-bot">{msg_html}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="label-user">Tú ✉️</div><div class="bubble-user">{msg_html}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  CONVERSATION LOOP
# ─────────────────────────────────────────────
if not st.session_state.done:
    current_step = st.session_state.step
    if current_step < len(STEPS):
        step_info  = STEPS[current_step]
        user_input = st.text_input(step_info["label"], key=f"input_{current_step}")

        if st.button("Enviar ➤"):
            if user_input.strip():
                st.session_state.chat_history.append(("user", user_input.strip()))
                st.session_state.lead[step_info["key"]] = user_input.strip()

                next_step = current_step + 1

                if next_step < len(STEPS):
                    st.session_state.chat_history.append(("bot", STEPS[next_step]["question"]))
                    st.session_state.step = next_step
                else:
                    score = score_lead(st.session_state.lead)
                    st.session_state.lead["score"] = score
                    save_lead(st.session_state.lead)

                    name    = st.session_state.lead.get("name", "Cliente")
                    closing = f"¡Gracias, {name}! Hemos registrado tu información. En breve uno de nuestros agentes se pondrá en contacto contigo."
                    st.session_state.chat_history.append(("bot", closing))
                    st.session_state.done = True

                st.rerun()
            else:
                st.warning("Por favor escribe una respuesta antes de continuar.")

# ─────────────────────────────────────────────
#  COMPLETION
# ─────────────────────────────────────────────
if st.session_state.done:
    if st.button("🔄 Nueva Conversación"):
        for key in ["step", "chat_history", "lead", "done", "greeted"]:
            del st.session_state[key]
        st.rerun()
