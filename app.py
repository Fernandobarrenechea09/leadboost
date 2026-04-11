import streamlit as st
from supabase import create_client
from datetime import datetime
import anthropic
import json

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
#  CONNECTIONS
# ─────────────────────────────────────────────
@st.cache_resource
def get_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

@st.cache_resource
def get_claude():
    return anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_KEY"])

# ─────────────────────────────────────────────
#  SYSTEM PROMPT FOR CLAUDE
# ─────────────────────────────────────────────
SYSTEM_PROMPT = """Eres LeadBoost, un asistente inmobiliario virtual para agencias de bienes raíces en Bolivia. Tu trabajo es tener una conversación natural en español con potenciales compradores o arrendatarios de propiedades y recopilar la siguiente información:

1. Nombre completo
2. Tipo de propiedad (Casa, Departamento, Terreno, Local comercial)
3. Zona o barrio de preferencia
4. Presupuesto aproximado en dólares
5. Plazo en meses para comprar o rentar
6. Número de teléfono

Reglas importantes:
- Conversa de forma natural y amigable en español
- Haz las preguntas de forma conversacional, no como un formulario
- Si el usuario da múltiple información en un solo mensaje, extráela toda
- Cuando tengas TODA la información, responde con un JSON al final de tu mensaje en este formato exacto:
  LEAD_COMPLETO:{"name":"...","property_type":"...","area":"...","budget":"...","timeline":"...","phone":"..."}
- Solo incluye LEAD_COMPLETO cuando tengas los 6 datos completos
- Mantén un tono profesional pero cálido
- Si el usuario escribe en español informal, responde igual de informalmente"""

# ─────────────────────────────────────────────
#  SESSION STATE INIT
# ─────────────────────────────────────────────
if "chat_history"    not in st.session_state: st.session_state.chat_history    = []
if "messages"        not in st.session_state: st.session_state.messages        = []
if "done"            not in st.session_state: st.session_state.done            = False
if "greeted"         not in st.session_state: st.session_state.greeted         = False

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
#  GET AI RESPONSE
# ─────────────────────────────────────────────
def get_ai_response(messages):
    try:
        claude   = get_claude()
        response = claude.messages.create(
            model      = "claude-haiku-4-5-20251001",
            max_tokens = 1000,
            system     = SYSTEM_PROMPT,
            messages   = messages
        )
        return response.content[0].text
    except Exception as e:
        return f"Lo siento, hubo un error. Por favor intenta de nuevo. ({e})"

# ─────────────────────────────────────────────
#  CHECK IF LEAD IS COMPLETE
# ─────────────────────────────────────────────
def extract_lead(response_text):
    if "LEAD_COMPLETO:" in response_text:
        try:
            json_str = response_text.split("LEAD_COMPLETO:")[1].strip()
            lead     = json.loads(json_str)
            return lead
        except:
            return None
    return None

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
    greeting = "👋 ¡Hola! Soy LeadBoost, tu asistente inmobiliario virtual. Estoy aquí para ayudarte a encontrar la propiedad perfecta en Bolivia. ¿Me puedes decir tu nombre y qué tipo de propiedad estás buscando?"
    st.session_state.chat_history.append(("bot", greeting))
    st.session_state.messages.append({"role": "assistant", "content": greeting})
    st.session_state.greeted = True

# ─────────────────────────────────────────────
#  RENDER CHAT HISTORY
# ─────────────────────────────────────────────
st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)
for sender, msg in st.session_state.chat_history:
    # Hide the LEAD_COMPLETO JSON from user
    display_msg = msg.split("LEAD_COMPLETO:")[0].strip() if "LEAD_COMPLETO:" in msg else msg
    msg_html    = display_msg.replace("\n", "<br>")
    if sender == "bot":
        st.markdown(f'<div class="label-bot">🤖 LeadBoost</div><div class="bubble-bot">{msg_html}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="label-user">Tú ✉️</div><div class="bubble-user">{msg_html}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  CONVERSATION LOOP
# ─────────────────────────────────────────────
if not st.session_state.done:
    user_input = st.text_input("Escribe tu mensaje...", key=f"input_{len(st.session_state.messages)}")

    if st.button("Enviar ➤"):
        if user_input.strip():
            # Add user message
            st.session_state.chat_history.append(("user", user_input.strip()))
            st.session_state.messages.append({"role": "user", "content": user_input.strip()})

            # Get AI response
            ai_response = get_ai_response(st.session_state.messages)

            # Add AI response to history
            st.session_state.chat_history.append(("bot", ai_response))
            st.session_state.messages.append({"role": "assistant", "content": ai_response})

            # Check if lead is complete
            lead = extract_lead(ai_response)
            if lead:
                score        = score_lead(lead)
                lead["score"] = score
                save_lead(lead)
                st.session_state.done = True

            st.rerun()
        else:
            st.warning("Por favor escribe un mensaje antes de continuar.")

# ─────────────────────────────────────────────
#  COMPLETION
# ─────────────────────────────────────────────
if st.session_state.done:
    if st.button("🔄 Nueva Conversación"):
        for key in ["chat_history", "messages", "done", "greeted"]:
            del st.session_state[key]
        st.rerun()
